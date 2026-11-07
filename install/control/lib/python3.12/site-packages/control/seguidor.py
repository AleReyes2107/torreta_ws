#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import time

class TrackerPID(Node):
    def __init__(self):
        super().__init__('seguidor_node')
        
        self.sub = self.create_subscription(Point, '/vision/ball_position', self.position_callback, 10)
        self.pub = self.create_publisher(JointTrajectory, '/pan_tilt_controller/joint_trajectory', 10)
        
        # --- Parámetros de sintonización PID ---
        # Si el movimiento es muy lento, sube el P. Si oscila mucho, baja el P y sube el D.
        self.kp_pan = 0.0008
        self.kd_pan = 0.0004
        
        self.kp_tilt = 0.0008
        self.kd_tilt = 0.0004
        
        # Estado anterior para la derivada
        self.prev_error_pan = 0.0
        self.prev_error_tilt = 0.0
        self.last_time = time.time()
        
        # Posición virtual actual (Iniciamos donde tu Arduino inicializa: Pan 90°, Tilt 45°)
        self.current_pan_rad = 0.0       # 0.0 rad = 90° en tu script de Arduino
        self.current_tilt_rad = -0.785   # -0.785 rad = 45° en tu script de Arduino
        
        self.get_logger().info("Controlador PID de seguimiento iniciado.")
        
    def position_callback(self, msg):
        if msg.z == 0.0:
            # "No hay nada" - Mantenemos la posición actual para no volvernos locos
            # Opcionalmente podrías programar aquí que regrese al centro después de X segundos
            return
            
        # 1. Calcular Errores (Centro de imagen: 320x240)
        # Si la cámara está al revés o el servo gira invertido, cambia el signo de estas restas
        error_pan = 320.0 - msg.x
        error_tilt = 240.0 - msg.y
        
        # 2. Calcular Tiempo Transcurrido (Derivada)
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0:
            dt = 0.01
            
        d_pan = (error_pan - self.prev_error_pan) / dt
        d_tilt = (error_tilt - self.prev_error_tilt) / dt
        
        # 3. Calcular Delta de Movimiento
        delta_pan = (self.kp_pan * error_pan) + (self.kd_pan * d_pan)
        delta_tilt = (self.kp_tilt * error_tilt) + (self.kd_tilt * d_tilt)
        
        # 4. Actualizar Posición
        self.current_pan_rad += delta_pan
        self.current_tilt_rad += delta_tilt
        
        # 5. Restricción preventiva de seguridad (Límites mecánicos de tu FutBot)
        # Pan: 0.0 a 1.57 (90° a 180° grados absolutos)
        self.current_pan_rad = max(0.0, min(1.57, self.current_pan_rad))
        # Tilt: -1.57 a 0.0 (0° a 90° grados absolutos)
        self.current_tilt_rad = max(-1.57, min(0.0, self.current_tilt_rad))
        
        # 6. Guardar estado
        self.prev_error_pan = error_pan
        self.prev_error_tilt = error_tilt
        self.last_time = current_time
        
        # 7. Armar y enviar el mensaje final al nodo del Arduino
        traj_msg = JointTrajectory()
        traj_msg.joint_names = ['pan_joint', 'tilt_joint']
        
        point = JointTrajectoryPoint()
        point.positions = [self.current_pan_rad, self.current_tilt_rad]
        traj_msg.points.append(point)
        
        self.pub.publish(traj_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TrackerPID()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
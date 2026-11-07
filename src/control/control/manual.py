#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import sys
import termios
import tty
import select

class ManualTeleop(Node):
    def __init__(self):
        super().__init__('manual_teleop')
        
        self.publisher_ = self.create_publisher(JointTrajectory, '/pan_tilt_controller/joint_trajectory', 10)
        
        # Posiciones iniciales (0.0 rad = 90 grados en tu Arduino)
        self.pan_pos = 0.0
        self.tilt_pos = 0.0
        self.step = 0.05 # Aproximadamente 2.8 grados por cada toque de tecla
        
        print("========================================")
        print("🎮 CONTROL MANUAL DE TORRETA (PRUEBA)")
        print("Teclas configuradas:")
        print("  4 / 5 : Girar Base (Pan)")
        print("  7 / 8 : Subir/Bajar Elevación (Tilt)")
        print("  q     : Salir")
        print("========================================")

    def publish_position(self):
        # LÍMITES DE SEGURIDAD FÍSICOS
        # La base gira libre de -90 a 90 grados (-1.5708 a 1.5708 rad)
        self.pan_pos = max(-1.5708, min(1.5708, self.pan_pos))
        # El cabeceo topado en -0.75 rad hacia atrás (como estaba en el original)
        self.tilt_pos = max(-0.75, min(1.5708, self.tilt_pos)) 

        # Empaquetar y enviar el comando
        traj_msg = JointTrajectory()
        traj_msg.joint_names = ['pan_joint', 'tilt_joint']
        traj_msg.header.stamp = self.get_clock().now().to_msg()
        
        point = JointTrajectoryPoint()
        point.positions = [self.pan_pos, self.tilt_pos]
        point.time_from_start = Duration(sec=0, nanosec=100000000) 
        
        traj_msg.points.append(point)
        self.publisher_.publish(traj_msg)
        
        # Imprimir telemetría en la misma línea
        sys.stdout.write(f"\r\033[K[TELEMETRÍA] Pan: {self.pan_pos:.2f} rad | Tilt: {self.tilt_pos:.2f} rad")
        sys.stdout.flush()

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    # Timeout de 0.05 segundos para no bloquear el bucle de ROS
    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main(args=None):
    rclpy.init(args=args)
    node = ManualTeleop()
    settings = termios.tcgetattr(sys.stdin)

    try:
        # Publicar una vez al iniciar para posicionar en el centro
        node.publish_position()

        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.01) 
            
            key = get_key(settings)
            
            if key == '':
                continue 
                
            if key == '4':
                node.pan_pos += node.step
                node.publish_position()
            elif key == '5':
                node.pan_pos -= node.step
                node.publish_position()
            elif key == '8': # Invertir suma/resta según te convenga
                node.tilt_pos += node.step
                node.publish_position()
            elif key == '7':
                node.tilt_pos -= node.step
                node.publish_position()
            elif key == 'q' or key == '\x03':  # 'q' o Ctrl+C para salir
                break
                
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()
        print("\nControl manual finalizado.")

if __name__ == '__main__':
    main()
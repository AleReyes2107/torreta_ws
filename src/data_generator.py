import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import time
from datetime import datetime

class AutoDataGeneratorNode(Node):
    def __init__(self):
        super().__init__('auto_data_generator_node')
        
        # Usando la carpeta de tu dataset
        self.save_dir = os.path.expanduser('~/torreta_ws/dataset_med')
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.bridge = CvBridge()
        self.image_count = 0
        
        # --- PARÁMETRO DE AUTOMATIZACIÓN ---
        # Tiempo en segundos entre cada captura (0.5 = dos fotos por segundo)
        self.capture_interval_sec = 0.5 
        self.last_save_time = time.time()
        
        self.subscription = self.create_subscription(
            Image,
            '/camera_mipi0/image_raw',
            self.image_callback,
            10
        )
        
        self.get_logger().info(f"Nodo iniciado. Guardando en: {self.save_dir}")
        self.get_logger().info(f"Capturando fotos AUTOMÁTICAMENTE cada {self.capture_interval_sec} segundos.")
        self.get_logger().info("Presiona Ctrl+C en esta terminal para detener la recolección.")

    def image_callback(self, msg):
        current_time = time.time()
        
        # Solo guarda si ha pasado el intervalo de tiempo establecido
        if (current_time - self.last_save_time) >= self.capture_interval_sec:
            try:
                cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            except Exception as e:
                self.get_logger().error(f"Error en cv_bridge: {e}")
                return

            # Generar nombre y guardar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = os.path.join(self.save_dir, f"muestra_med_{timestamp}.jpg")
            
            cv2.imwrite(filename, cv_image)
            self.image_count += 1
            self.get_logger().info(f"[{self.image_count}] Foto auto-guardada.")
            
            # Actualizar el reloj para la siguiente captura
            self.last_save_time = current_time

def main(args=None):
    rclpy.init(args=args)
    node = AutoDataGeneratorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("\nRecolección automática terminada.")
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
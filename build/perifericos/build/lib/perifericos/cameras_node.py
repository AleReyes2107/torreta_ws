import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import os  

class CameraMipiNode(Node):
    def __init__(self):
        super().__init__('camera_mipi0_node')
        
        # Parámetros por defecto
        self.declare_parameter('video_device', '/dev/video8')
        self.declare_parameter('frame_id', 'camera_mipi0_optical_frame')
        
        video_device = self.get_parameter('video_device').value
        self.frame_id = self.get_parameter('frame_id').value
        
        # Traducir la regla UDEV 
        if os.path.islink(video_device):
            video_real = os.path.realpath(video_device)
            self.get_logger().info(f'Regla UDEV resuelta: {video_device} -> {video_real}')
            video_device = video_real
        
        # Publicadores
        self.image_pub = self.create_publisher(Image, 'image_raw', 10)
        self.info_pub = self.create_publisher(CameraInfo, 'camera_info', 10)
        
        self.bridge = CvBridge()
        
        # OpenCV recibe el puerto 
        self.cap = cv2.VideoCapture(video_device, cv2.CAP_V4L2)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            self.get_logger().error(f'Fallo al abrir el puerto MIPI: {video_device}')
            return
            
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
        self.get_logger().info(f'Nodo iniciado. Publicando video de {video_device} como {self.frame_id}')

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # Capturar el timestamp exacto
            msg_time = self.get_clock().now().to_msg()
            
            # Construir el mensaje de imagen
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            img_msg.header.stamp = msg_time
            img_msg.header.frame_id = self.frame_id
            
            # Construir el mensaje de información de cámara
            info_msg = CameraInfo()
            info_msg.header.stamp = msg_time
            info_msg.header.frame_id = self.frame_id
            info_msg.width = 640
            info_msg.height = 480
            
            # Publicar ambos tópicos sincronizados
            self.image_pub.publish(img_msg)
            self.info_pub.publish(info_msg)

def main(args=None):
    rclpy.init(args=args)
    node = CameraMipiNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cap.release()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
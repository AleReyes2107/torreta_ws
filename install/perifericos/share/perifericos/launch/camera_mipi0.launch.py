from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='perifericos',
            executable='cameras_node',
            name='camera_mipi0_node',
            namespace='camera_mipi0',
            output='screen',
            prefix=['libcamerify'],
            parameters=[{
                # Ruta permanente para el MIPI 0
                'video_device': '/dev/v4l/by-path/platform-1f00110000.csi-video-index0',
                'frame_id': 'camera_mipi0_optical_frame'
            }]
        )
    ])
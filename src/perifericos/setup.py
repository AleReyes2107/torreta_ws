import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'perifericos'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Copia todos los archivos de la carpeta launch
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Alejandro Reyes',
    maintainer_email='tu_correo@ejemplo.com',
    description='Paquete de periféricos para torreta y control',
    license='Apache-2.0', # Ajusta a la licencia que estés usando
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Formato: nombre_del_ejecutable = nombre_paquete.nombre_archivo_sin_py:funcion_main
            'cameras_node = perifericos.cameras_node:main',
            'arduino_node = perifericos.arduino_node:main',
        ],
    },
)
from setuptools import setup, find_packages

setup(
    name='drone_2d_custom_gym_env',
    version='1.0.0',
    description='2D drone custom Gym environment for reinforcement learning (pink drone edition)',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['gym', 'pygame', 'pymunk', 'numpy', 'stable-baselines3[extra]'],
)

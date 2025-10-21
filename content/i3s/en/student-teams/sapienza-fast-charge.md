# Sapienza Fast Charge

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **About this page**

For the content of this page, we have directly involved the team discussed, which corresponds to their presentation of it.
{{% /hint %}}

**Sapienza Fast Charge** is the Formula Student Electric team of Sapienza University. Our team brings together academic expertise and hands-on skills to design, build, and race high-performance electric single-seater cars. Our mission is to push the boundaries of electric vehicle technology and champion sustainable racing practices.

## DV Car 2024

### Overview

The **DV Car 2024** is our latest advancement in electric and autonomous vehicle design, reflecting two years of dedicated development. This autonomous, driverless electric vehicle integrates advanced sensor technology and cutting-edge software solutions, tackling challenges in autonomous control with promising results.

### Key Components

#### Microservices Architecture

Our software is structured using a **microservices-based architecture**, where each primary task for autonomous driving runs within its own dedicated service. These services operate independently but communicate through a message broker. This architecture ensures:

- Efficient resource allocation for parallel processing
- Robustness against critical failures, as one microservice failure does not affect the entire system

#### Key Microservices

1. **Computer Vision**:  
   The computer vision module identifies track cones using a depth camera that leverages infrared sensors to measure cone distances. Key functionalities include:
   - **Cone Detection**: Determines cone positions in space
   - **Color Recognition**: Essential for trajectory estimation
   - **Error Filtering**: Discards cones with irregular color or distance readings

2. **Sensor Fusion & SLAM (Simultaneous Localization and Mapping)**:  
   This system integrates data from multiple sensors—accelerometer, gyroscope, magnetometer, GPS, and Lidar—for precise navigation. SLAM performs two main tasks:
   - **Mapping**: Constructs a map using sensor data and cone positions identified by computer vision
   - **Localization**: Determines the car's current position on the map, allowing for real-time trajectory planning

3. **Path Planning**:  
   This component uses cone data from computer vision to calculate a safe, efficient path for the car, minimizing lap time. It incorporates techniques such as triangulations and interpolations to optimize the path.

4. **High-Level Control (HLC)**:  
   HLC coordinates actuator functions (steering, throttle, and brakes) based on inputs from the path planner and SLAM. This module employs deep reinforcement learning algorithms to fine-tune control signals for accurate trajectory following.

### Future Outlook

Sapienza Fast Charge is continuously innovating in electric and autonomous vehicle technology. With ongoing research and development, we aim to elevate performance, enhance safety, and contribute to the sustainable future of motorsport.

---

**Join us** in this exciting journey at the frontier of sustainable, high-tech racing!

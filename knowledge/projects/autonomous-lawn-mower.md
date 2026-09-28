---
project_name: "Intelligent System for Lawn Mowers (Autonomous Intelligent Lawn Mower)"
short_description: "Autonomous robotic lawn mower for flat, dry fields integrating edge computer vision (YOLOv26n INT8 TFLite), multi-sensor fusion (ultrasonic, MPU6050 IMU, odometry), and an independent ATmega safety watchdog controller."
problem: "Traditional lawn mowing requires continuous human operation; autonomous systems must handle navigation and obstacle avoidance safely without relying exclusively on high-level computers that can freeze, hang, or crash."
solution: "Engineered a layered cyber-physical architecture: Raspberry Pi 4 handles high-level perception, YOLOv26n INT8 TFLite inference, and navigation planning, while an independent ATmega microcontroller acts as a real-time safety watchdog monitoring a 500ms heartbeat with manual override and emergency stop."
architecture: "Hierarchical edge cyber-physical architecture: Raspberry Pi 4 (4 GB RAM, 64 GB microSD) for high-level computer vision and navigation; ATmega microcontroller as independent hardware safety watchdog monitoring continuous ~500 ms heartbeat; 3 × ultrasonic sensors + MPU6050 IMU + odometry for proximity and motion sensing; 12 V 755 DC drive motors on a 4–5 kg payload chassis."
technologies:
  - "Raspberry Pi 4 (4 GB RAM)"
  - "ATmega Microcontroller"
  - "YOLOv26n"
  - "TensorFlow Lite"
  - "INT8 Quantization"
  - "MPU6050 IMU"
  - "Ultrasonic Sensors (3×)"
  - "755 12 V DC Motors"
  - "Odometry"
  - "AprilTags (Considered)"
  - "Python"
  - "C / Embedded C"
programming_languages:
  - "Python"
  - "C / C++"
frameworks:
  - "TensorFlow Lite"
models:
  - "YOLOv26n (INT8 TFLite quantized)"
databases: []
infrastructure:
  - "Raspberry Pi 4 (4 GB RAM)"
  - "ATmega Microcontroller"
  - "64 GB MicroSD"
exact_contribution: "Architected the cyber-physical system, implemented the edge AI perception pipeline using INT8 quantized YOLOv26n on TFLite, integrated 3× ultrasonic and MPU6050 sensor fusion, designed the 500 ms heartbeat watchdog communication between Raspberry Pi and ATmega safety controller, and adapted the platform from Pi 5 to Pi 4 under strict compute/memory constraints."
responsibilities:
  - "Designed and implemented layered edge robotics architecture separating high-level perception (Raspberry Pi 4) from low-level safety (ATmega watchdog)."
  - "Trained, converted, and deployed YOLOv26n object detection model with INT8 quantization via TensorFlow Lite for edge inference on Raspberry Pi."
  - "Built sensor fusion and navigation logic integrating 3 × ultrasonic sensors for proximity detection, MPU6050 IMU, and motor odometry."
  - "Implemented 500 ms heartbeat watchdog protocol between Raspberry Pi and ATmega safety controller with automatic safe-state fallback, manual override, and emergency stop."
  - "Engineered mechanical and electrical integration for 4–5 kg chassis powered by 12 V 755 DC drive motors."
results:
  - "Successfully deployed real-time INT8 quantized YOLOv26n object detection on Raspberry Pi 4 edge hardware."
  - "Established fail-safe operation with ATmega watchdog halting drive motors within 500 ms of any compute hang or software crash."
  - "Successfully adapted entire software and ML stack from Raspberry Pi 5 to Raspberry Pi 4 (4 GB RAM) following hardware theft before final presentation."
metrics:
  - ">95% obstacle avoidance target"
  - "500 ms watchdog heartbeat timeout"
  - "4–5 kg system payload target"
  - "12 V motor operating voltage"
github_url: "https://github.com/Jaykay73"
live_demo_url: ""
screenshots: []
challenges: "Hardware replacement constraint after original Raspberry Pi 5 was stolen prior to final presentation, requiring optimization of vision models to run reliably on Raspberry Pi 4 (4 GB RAM) via INT8 TFLite; eliminating single point of failure in physical safety through an independent microcontroller watchdog."
technical_decisions: "Selected YOLOv26n nano variant with INT8 quantization to satisfy tight edge CPU/RAM constraints; decoupled physical safety into an ATmega watchdog controller with 500 ms heartbeat rather than trusting the Linux OS for motor safety; combined ultrasonic proximity sensing with vision for robust obstacle detection."
lessons_learned: "Cyber-physical systems must never rely solely on an OS-level computer for physical machine safety; edge AI requires strict hardware-aware quantization and multi-modal sensor redundancy."
deployment_information: "Edge deployment on Raspberry Pi 4 (4 GB RAM, 64 GB SD card) paired with ATmega microcontroller on physical 4–5 kg mower chassis."
deployment_platform: "Edge / Embedded (Raspberry Pi 4 + ATmega)"
relevant_domains:
  - "Autonomous Robotics"
  - "Edge AI / Embedded Systems"
  - "Computer Vision"
  - "Cyber-Physical Systems"
  - "Safety Engineering"
relevant_job_titles:
  - "Robotics Engineer"
  - "Embedded AI Engineer"
  - "Edge ML Engineer"
  - "Computer Vision Engineer"
  - "AI / Systems Engineer"
keywords:
  - "YOLOv26n"
  - "TensorFlow Lite"
  - "INT8 Quantization"
  - "Raspberry Pi"
  - "ATmega"
  - "Watchdog"
  - "Heartbeat"
  - "Ultrasonic Sensors"
  - "MPU6050 IMU"
  - "Odometry"
  - "Autonomous Navigation"
  - "Obstacle Avoidance"
  - "Edge AI"
dates: "2025 – 2026"
status: "completed"
---

# Autonomous Intelligent Lawn Mower — Project Knowledge Base

## 1. Project Identity

**Project Name:** Intelligent System for Lawn Mowers  
**Project Type:** Autonomous robotics / embedded systems / computer vision / machine learning  
**Primary Goal:** Develop an intelligent robotic lawn mower capable of autonomously navigating a flat, dry grass field, detecting and avoiding obstacles, and mowing the environment while allowing a human operator to intervene when necessary.

The project combines:

* Embedded systems
* Robotics
* Computer vision
* Machine learning
* Autonomous navigation
* Motor control
* Sensor fusion
* Safety systems
* Wireless/app-based control

The project was developed as a final-year engineering project.

---

## 2. Problem Statement

Traditional lawn mowing requires continuous human operation. The objective of this project was to develop an intelligent lawn mower that can perform mowing tasks autonomously while maintaining sufficient safety and allowing human intervention.

The system was designed for relatively **flat, dry fields**, rather than highly uneven or wet terrain.

The mower needed to:

1. Move autonomously around the field.
2. Detect obstacles in its path.
3. Avoid obstacles instead of colliding with them.
4. Continue its mowing task after obstacle avoidance.
5. Allow manual control when necessary.
6. Provide an emergency/stop mechanism.
7. Maintain reliable low-level motor control.
8. Detect failures in the main computing system.
9. Use computer vision where appropriate for environmental perception.

---

## 3. Core System Concept

The mower follows a layered architecture.

### High-level intelligence

A Raspberry Pi performs computationally intensive tasks such as:

* Computer vision
* Object detection
* High-level navigation
* Decision making
* Communication with the control interface

### Low-level control

An **ATmega microcontroller** handles safety-critical and timing-sensitive functions such as:

* Motor/control interfacing
* Watchdog functionality
* Monitoring communication from the Raspberry Pi
* Maintaining safe behavior if the main computer becomes unresponsive

This creates a separation between:

**AI / perception / high-level decision making**

and

**real-time embedded control / safety.**

---

## 4. Hardware Architecture

### 4.1 Main Computer

#### Raspberry Pi

The original project was intended to use a **Raspberry Pi 5**.

However, the Raspberry Pi 5 was stolen before the final presentation.

A **Raspberry Pi 4 with 4 GB RAM** was subsequently used as the replacement platform.

The replacement system used:

* Raspberry Pi 4
* 4 GB RAM
* 64 GB microSD card

This hardware constraint was important because the computer vision and machine-learning components had to operate on relatively limited edge-computing hardware.

---

## 5. Computer Vision

The project uses an object-detection model for visual perception.

### Model

**YOLOv26n**

The selected model is the **nano/small-footprint variant**, making it more appropriate for edge deployment than a significantly larger YOLO model.

The model was converted/deployed using:

**TensorFlow Lite (TFLite)**

with:

**INT8 quantization**

The purpose of INT8 quantization was to reduce computational and memory requirements and make inference more practical on Raspberry Pi hardware.

---

## 6. Why Edge AI Was Used

The mower was intended to make decisions locally rather than depending on a remote server.

This provides several advantages:

* Reduced network dependency
* Lower communication latency
* Operation when internet access is unavailable
* Better privacy
* More reliable autonomous operation
* Ability to make decisions directly on the robot

The trade-off is that the ML model must be sufficiently lightweight to operate on the Raspberry Pi.

This was one reason for using a lightweight YOLO model and INT8 TFLite deployment.

---

## 7. Obstacle Detection and Avoidance

One of the major functional requirements was autonomous obstacle avoidance.

The target requirement was:

**> Greater than 95% obstacle avoidance performance.**

The system combines different sensing modalities rather than relying exclusively on computer vision.

### Sensors

The mower uses:

* **3 × ultrasonic sensors**
* **MPU6050 IMU**
* Camera/computer vision system

The ultrasonic sensors provide direct distance measurements to nearby obstacles.

The IMU provides information about the mower's motion/orientation.

Computer vision provides higher-level environmental information.

---

## 8. Ultrasonic Sensor Configuration

Three ultrasonic sensors are used to provide spatial coverage around the mower.

The arrangement is intended to allow the system to determine whether an obstacle is present in different portions of its forward environment.

Conceptually:

```text
             FRONT
               ↑

       [Ultrasonic]
             \

 [Ultrasonic]     [Ultrasonic]

        ┌───────────────┐
        │     MOWER     │
        └───────────────┘
```

The ultrasonic system provides a relatively simple and computationally inexpensive mechanism for detecting objects that are physically close to the mower.

This complements camera-based perception.

---

## 9. IMU

The mower uses an:

**MPU6050**

The MPU6050 combines:

* Accelerometer
* Gyroscope

The IMU can provide information useful for estimating:

* Orientation
* Angular movement
* Changes in motion
* Turning behavior
* Motion consistency

The IMU is particularly useful because wheel-based movement alone can accumulate errors, especially when the mower turns or experiences changes in traction.

---

## 10. Odometry

The navigation architecture considered/uses **odometry and IMU-based information** for estimating movement.

Odometry allows the system to estimate its position based on movement of the drive system.

Conceptually:

```text
Motor movement
      ↓
Wheel displacement
      ↓
Odometry estimate
      ↓
Position / movement estimate
      ↓
Navigation decision
```

However, odometry is subject to accumulated error.

For example:

* Wheel slip
* Uneven surfaces
* Motor differences
* Mechanical inaccuracies
* Turning errors

can cause the estimated position to diverge from the actual position.

This is why combining odometry with additional sensing is useful.

---

## 11. AprilTags — Considered Navigation Option

**AprilTags** were considered as a potential mechanism for localization.

AprilTags are visual fiducial markers that can provide known reference points to a robot equipped with a camera.

The basic concept would be:

```text
Camera
  ↓
Detect AprilTag
  ↓
Identify known reference
  ↓
Estimate robot position/orientation
  ↓
Correct navigation estimate
```

This was considered as an alternative/complement to relying purely on odometry and IMU measurements.

AprilTags were **considered**, rather than being treated as a core implemented component unless explicitly confirmed elsewhere.

---

## 12. Motor System

The mower uses:

**755 12 V DC motors**

The motors provide the mechanical drive system for the mower.

The target overall mower payload/system weight was approximately:

**4–5 kg**

The motor-control architecture needs to account for:

* Motor current
* Battery capacity
* PWM control
* Direction control
* Starting current
* Load variations
* Thermal considerations

---

## 13. ATmega Safety Controller

A particularly important aspect of the project is the use of an **ATmega microcontroller as a watchdog/safety layer**.

The Raspberry Pi is a powerful general-purpose computer, but it runs an operating system and can potentially:

* Freeze
* Crash
* Hang
* Lose communication
* Become overloaded

For a moving machine, relying entirely on the Raspberry Pi for safety is undesirable.

Therefore, the ATmega provides an independent low-level monitoring mechanism.

---

## 14. Raspberry Pi ↔ ATmega Heartbeat

The Raspberry Pi is expected to periodically send a **heartbeat signal** to the ATmega.

The target timeout is approximately:

**500 ms**

Conceptually:

```text
Raspberry Pi
     │
     │ heartbeat
     ↓
   ATmega
     │
     ├── heartbeat received
     │       ↓
     │    Continue operation
     │
     └── heartbeat missing
             ↓
          Timeout
             ↓
       Enter safe state
```

If the Raspberry Pi stops communicating for longer than the defined timeout, the ATmega can interpret this as a failure condition.

The safety controller can then prevent continued uncontrolled operation.

This is an important architectural principle:

> **The AI computer should not be the single point of failure for physical safety.**

---

## 15. Safety Architecture

The mower includes multiple layers of safety.

### Software-level safety

The Raspberry Pi can make decisions based on:

* Object detection
* Distance measurements
* Navigation state
* Sensor information

### Hardware-level safety

The ATmega provides an independent watchdog mechanism.

### Human intervention

The mower also includes:

* Manual override
* Stop functionality

This gives the system a hierarchy approximately like:

```text
             Human operator
                   │
          Manual override / STOP
                   │
                   ▼
        ┌─────────────────────┐
        │   Safety Controller  │
        │      (ATmega)        │
        └──────────┬──────────┘
                   │
             Safe motor state
                   │
                   ▼
        ┌─────────────────────┐
        │ Raspberry Pi / AI    │
        │ High-level control   │
        └──────────┬──────────┘
                   │
          Perception/navigation
                   │
                   ▼
             Motor system
```

---

## 16. User Control

Although the mower is autonomous, the design includes an external control interface.

The system supports:

### ON

Start the mower/system.

### OFF

Turn off the system.

### Manual Override

Allow the human operator to take control instead of relying on autonomous navigation.

### STOP

Provide a direct mechanism to stop operation.

The purpose of this hybrid architecture is to avoid treating autonomy as an all-or-nothing feature.

The mower can operate autonomously while retaining human control.

---

## 17. Proposed Operating Cycle

A typical autonomous cycle can be represented as:

```text
START
  ↓
Initialize system
  ↓
Initialize sensors
  ↓
Initialize Raspberry Pi
  ↓
Initialize ATmega communication
  ↓
Heartbeat established?
  │
  ├── NO → SAFE STATE
  │
  └── YES
        ↓
   Begin navigation
        ↓
Capture sensor data
        ↓
 ┌─────────────────────┐
 │ Camera / YOLO model │
 └──────────┬──────────┘
            ↓
     Object detection
            │
            ├──────────────┐
            │              │
            ↓              ↓
      No obstacle      Obstacle
            │              │
            ↓              ↓
      Continue path   Determine avoidance
                           │
                           ↓
                     Change direction
                           │
                           ↓
                     Avoid obstacle
                           │
                           ↓
                     Resume mowing
```

Throughout this process:

```text
Raspberry Pi ───── heartbeat ─────> ATmega
```

must remain active.

If the heartbeat fails:

```text
Heartbeat timeout
       ↓
ATmega detects failure
       ↓
Stop / safe motor state
```

---

## 18. ML Deployment Pipeline

The computer-vision pipeline can be represented as:

```text
Training Dataset
      ↓
Data Preparation
      ↓
YOLO Training
      ↓
Model Evaluation
      ↓
YOLO Model
      ↓
Conversion
      ↓
TensorFlow Lite
      ↓
INT8 Quantization
      ↓
Raspberry Pi
      ↓
Real-time inference
```

The important distinction is that the model was not intended to remain a desktop-only model.

The project specifically considered **edge deployment constraints**.

---

## 19. Engineering Constraints

The project had several significant constraints.

### Computational constraints

The Raspberry Pi 4 has substantially less computational capability than a desktop GPU.

Therefore:

* Model size matters.
* Inference speed matters.
* Memory usage matters.
* Quantization becomes valuable.
* Computationally expensive algorithms need to be minimized.

### Mechanical constraints

The mower must operate within a relatively small weight envelope:

**approximately 4–5 kg target.**

The motors therefore need to provide adequate torque while remaining compatible with the power system.

### Power constraints

The motors are:

**12 V**

which means the power architecture needs to account for the relatively high current requirements of DC motors compared with the Raspberry Pi and sensors.

### Safety constraints

A failure of the Raspberry Pi must not necessarily result in uncontrolled motor operation.

This motivated the independent ATmega watchdog.

---

## 20. System-Level Architecture

The overall architecture can be summarized as:

```text
                       ┌──────────────────┐
                       │  User Interface  │
                       │ ON/OFF/Override  │
                       │      /STOP       │
                       └────────┬─────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │    Raspberry Pi 4    │
                    │       4 GB RAM       │
                    ├──────────────────────┤
                    │ Computer Vision      │
                    │ YOLOv26n             │
                    │ TFLite INT8          │
                    │ Navigation            │
                    │ Decision Making       │
                    └──────────┬───────────┘
                               │
                      Heartbeat / Commands
                               │
                               ▼
                    ┌──────────────────────┐
                    │       ATmega         │
                    │ Safety / Watchdog    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Motor Control     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    755 DC Motors     │
                    │        12 V          │
                    └──────────────────────┘


Sensors
──────────────

Camera ──────────────> Raspberry Pi
3× Ultrasonic ───────> Raspberry Pi / Control System
MPU6050 IMU ─────────> Raspberry Pi / Control System
```

---

## 21. Key Technical Components

| Component                      | Technology                  | Purpose                             |
| ------------------------------ | --------------------------- | ----------------------------------- |
| Main computer                  | Raspberry Pi 4, 4 GB        | AI, perception, navigation          |
| Original planned computer      | Raspberry Pi 5              | Intended primary computing platform |
| Storage                        | 64 GB SD card               | OS, models, software and data       |
| Vision model                   | YOLOv26n                    | Object detection                    |
| ML runtime                     | TensorFlow Lite             | Edge inference                      |
| Quantization                   | INT8                        | Reduce computational requirements   |
| Microcontroller                | ATmega                      | Low-level safety/watchdog           |
| Distance sensors               | 3 × ultrasonic              | Proximity/obstacle detection        |
| IMU                            | MPU6050                     | Motion/orientation sensing          |
| Drive motors                   | 755, 12 V                   | Physical locomotion                 |
| Localization option            | Odometry + IMU              | Movement estimation                 |
| Localization option considered | AprilTags                   | Visual reference/localization       |
| User controls                  | ON/OFF/manual override/STOP | Human intervention                  |

---

## 22. Important Design Decisions

### Lightweight ML model

A lightweight YOLO model was selected because the system needed to run on an edge device rather than a high-performance GPU.

### TFLite deployment

TensorFlow Lite provides a deployment-oriented runtime suitable for constrained hardware.

### INT8 quantization

INT8 quantization reduces model computational requirements and can improve inference efficiency on edge hardware, at the potential cost of some model accuracy.

### Multiple sensors

Using computer vision alongside ultrasonic sensing reduces dependence on a single sensing technology.

### Independent watchdog

The ATmega provides a safety mechanism independent of the Raspberry Pi.

### Manual override

The system retains human control rather than requiring complete reliance on autonomous behavior.

---

## 23. Challenges Encountered

### Raspberry Pi 5 loss

The original Raspberry Pi 5 was stolen before the project presentation.

This forced the project to transition to:

**Raspberry Pi 4, 4 GB RAM**

with:

**64 GB SD card.**

This introduced a more constrained computational environment and reinforced the importance of lightweight ML deployment.

### Edge inference

Running computer vision on Raspberry Pi hardware requires consideration of:

* Model size
* Inference latency
* RAM usage
* Thermal behavior
* Power consumption

This motivated the use of YOLOv26n and INT8 TFLite.

### Autonomous safety

Because the machine is physically mobile, a software crash cannot simply be treated like a normal application crash.

The ATmega watchdog architecture was therefore incorporated to provide an independent failure-detection mechanism.

### Localization

Odometry provides movement estimation but can accumulate error.

The project therefore considered combining odometry and IMU information, with AprilTags considered as a possible additional localization/reference mechanism.

---

## 24. Project Engineering Philosophy

The project is not simply an ML model mounted on a lawn mower.

It is a **cyber-physical system** combining:

```text
Machine Learning
      +
Computer Vision
      +
Robotics
      +
Embedded Systems
      +
Sensor Fusion
      +
Real-Time Control
      +
Safety Engineering
      +
Human-Machine Interaction
```

The ML component provides perception, but the final system requires considerably more engineering around the model.

A successful autonomous mower must integrate:

1. Perception
2. Localization
3. Planning
4. Control
5. Actuation
6. Safety
7. Human intervention

---

## 25. Skills Demonstrated

This project demonstrates experience with:

### Machine Learning

* Object detection
* YOLO
* Model deployment
* Model optimization
* Quantization
* Edge AI

### Computer Vision

* Camera-based perception
* Object detection
* Potential visual localization using AprilTags

### Robotics

* Autonomous navigation
* Obstacle avoidance
* Odometry
* Sensor integration
* Motor control

### Embedded Systems

* Raspberry Pi
* ATmega microcontrollers
* Watchdog systems
* Hardware/software communication
* Real-time safety considerations

### Systems Engineering

* Hardware constraints
* Computational constraints
* Power constraints
* Fault tolerance
* Human override
* Safety architecture

---

## 26. Current/Final Hardware Situation

The originally intended computing platform was:

**Raspberry Pi 5**

However, because the Pi 5 was stolen before the presentation, the project was adapted to:

**Raspberry Pi 4 — 4 GB RAM**  
**64 GB SD card**

The remainder of the system was designed around the constrained replacement platform.

This adaptation is itself an important part of the project's engineering history: the system had to be made viable under a significant hardware constraint rather than abandoning the project.

---

## 27. Project Status Classification

The following distinction should be maintained when describing this project to an AI assistant, interviewer, CV generator, or job-application system.

### Implemented / Core project

* Autonomous lawn-mower concept
* Raspberry Pi-based computing
* YOLO-based computer vision
* Lightweight YOLO model
* TensorFlow Lite deployment
* INT8 model optimization
* Ultrasonic obstacle sensing
* MPU6050 IMU
* ATmega watchdog architecture
* Heartbeat monitoring
* Manual override
* Stop functionality
* ON/OFF controls
* 755 12 V motors

### Considered / explored

* AprilTags for localization
* More advanced sensor-fusion/localization approaches

### Hardware change

* Raspberry Pi 5 was originally intended.
* Raspberry Pi 5 became unavailable because it was stolen.
* Raspberry Pi 4 4 GB was used as the replacement.

### Target specification

* Flat, dry fields
* Approximately 4–5 kg system target
* Greater than 95% obstacle-avoidance target

The AI assistant should **not automatically describe the 95% obstacle-avoidance figure as a measured achieved result** unless an actual test result is supplied. It is currently best represented as a project requirement/target.

---

## 28. Short Project Description

The Intelligent System for Lawn Mowers is an autonomous robotic lawn mower designed for flat, dry fields. The system combines edge computer vision, machine learning, ultrasonic sensing, IMU-based motion sensing, autonomous navigation, and embedded safety control. A Raspberry Pi performs high-level perception and decision-making using an INT8 TensorFlow Lite implementation of YOLOv26n, while an ATmega provides an independent watchdog layer that monitors the Raspberry Pi through a heartbeat mechanism with a target timeout of approximately 500 ms. The mower uses three ultrasonic sensors, an MPU6050 IMU, odometry-based movement estimation, and 12 V 755 motors, while retaining manual override and stop functionality.

---

## 29. Interview-Level Explanation

If asked **"Tell me about your autonomous lawn mower project"**, the core explanation is:

> I developed an intelligent autonomous lawn mower that combines computer vision, embedded systems, and robotics. The main computer is a Raspberry Pi running a lightweight YOLOv26n object-detection model deployed with INT8 TensorFlow Lite for edge inference. I combined visual perception with three ultrasonic sensors and an MPU6050 IMU to support obstacle detection and navigation. One of the aspects I focused heavily on was safety: instead of allowing the Raspberry Pi to be the only controller, I introduced an ATmega microcontroller as an independent watchdog. The Raspberry Pi continuously sends a heartbeat, and if that heartbeat stops for roughly 500 milliseconds, the ATmega can trigger a safe state. The system also supports manual override and stopping. The original design used a Raspberry Pi 5, but after it was stolen before the final presentation, I adapted the system to a Raspberry Pi 4 with 4 GB RAM and a 64 GB SD card.

---

## 30. Knowledge-Base Instructions for an AI Assistant

When answering questions about this project:

1. Treat the project as an **autonomous robotic lawn mower**, not merely an object-detection project.
2. Identify the Raspberry Pi as the **high-level computing/AI platform**.
3. Identify the ATmega as the **independent low-level safety/watchdog controller**.
4. Remember that the Pi 5 was the original platform but was replaced by a Pi 4 4 GB after the Pi 5 was stolen.
5. Remember that the ML model is **YOLOv26n**, deployed using **TensorFlow Lite with INT8 quantization**.
6. Remember the mower uses **three ultrasonic sensors**.
7. Remember the IMU is an **MPU6050**.
8. Remember the drive motors are **755 12 V motors**.
9. Remember the target system weight was approximately **4–5 kg**.
10. Remember the intended operating environment is **flat, dry fields**.
11. Remember that **>95% obstacle avoidance** was a target requirement, not automatically an achieved measurement.
12. Remember that **odometry and IMU** were part of the navigation/localization approach.
13. Remember **AprilTags were considered**, but do not claim they were implemented unless additional information confirms this.
14. Remember the system supports **ON/OFF, manual override, and STOP**.
15. Do not invent datasets, accuracy figures, FPS measurements, training epochs, sensor arrangements, communication protocols, or test results that are not documented here.
16. When distinguishing project experience, separate **implemented features**, **planned features**, **considered technologies**, and **target specifications**.
17. The project should be presented as demonstrating competence across **ML, computer vision, robotics, embedded systems, edge AI, sensor integration, and safety engineering**.

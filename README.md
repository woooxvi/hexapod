# <img src="./imgs/hexapod-logo.svg" alt="logo" width="64"/> Hexapod

A Hexapod Robot using Raspberry Pi Zero W

![banner](imgs/banner.jpg)

## Introduction

This is a hexapod robot based on [Smallp Tsai](https://github.com/SmallpTsai)'s [hexapod-v2-7697](https://github.com/SmallpTsai/hexapod-v2-7697) project.
This project reused most of the mechanism design in the original project, but with a totally redesign on the circuits and softwares.
The table below shows the difference between this project and the original one.

|                 | Original hexapod-v2-7697 | This project                                    |
| --------------- | ------------------------ | ----------------------------------------------- |
| Controller      | Linkit 7697              | Raspberry Pi Zero W or Raspberry Pi Zero W 2    |
| PWM control     | Custom circuit board     | 2 x PCA9685 motor driver boards                 |
| DC-DC           | 7 x mini360 modules      | 2 x XL4005 5A Max DC-DC modules and 1 x mini360 |
| Power           | 2S Lipo battery          | 2 x 18650 batteries                             |
| Remote          | BLE                      | WiFi                                            |
| Remote software | Android and iOS          | PC, Android (WIP)                               |

## Instructions

1. [Mechanism](mechanism/) - How to build the body
1. [Electronics](electronics/) - Circuit explanation
1. [Software](software/) - The software running on Linkit 7697

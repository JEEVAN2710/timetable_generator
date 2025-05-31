<div align="center">

# 🎓 School Timetable Generator

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Gradio UI](https://img.shields.io/badge/Gradio-UI-orange.svg)](https://gradio.app/)
[![Pandas](https://img.shields.io/badge/Pandas-Data-red.svg)](https://pandas.pydata.org/)
[![License-MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

### 🚀 Streamline Your School Scheduling with AI-Powered Timetable Generation

[Features](#features-in-detail) · [Installation](#installation) · [Usage](#usage) · [Contributing](#contributing)

</div>

---

## 🌟 Overview

> Transform your school's scheduling process with our intelligent timetable generator. Built with Python and enhanced with a modern Gradio web interface, this tool automates the complex task of creating school schedules while following NCERT curriculum guidelines.

### 📝 Key Features

* **Smart Class Scheduling**: Automatically generates timetables for grades 1–12 with multiple sections
* **Teacher Management**: Efficiently handles teacher assignments and workload distribution
* **Activity Integration**: Seamlessly incorporates special activities and breaks
* **Conflict Resolution**: Automatically prevents scheduling conflicts
* **Customizable Time Slots**: Flexible scheduling from 7 AM to 4:50 PM
* **Modern UI**: Intuitive interface built with Gradio
* **Export Capability**: Generates organized CSV files for all timetables

### 🎯 Target Users

* School Administrators
* Academic Coordinators
* Department Heads
* Educational Institutions of All Sizes

## 🛠️ Technical Stack

| Component       | Technology  |
| --------------- | ----------- |
| Backend         | Python 3.8+ |
| UI Framework    | Gradio      |
| Data Processing | Pandas      |
| Export Formats  | CSV         |

## 💡 Features in Detail

### 📚 Academic Structure Support

* **Grade Levels**:

  * Primary (1–5)
  * Middle School (6–8)
  * Secondary (9–10)
  * Senior Secondary (11–12 with Science/Commerce/Arts streams)
* **Multiple Sections**: Support for sections A through H
* **Subject Categories**:

  * Core Subjects (Grade-specific NCERT curriculum)
  * Activity Subjects (Sports, Drawing/Craft, Drama, Music, etc.)

### ⚙️ Scheduling Capabilities

* **Flexible Timing**: Customizable time slots with 50-minute periods
* **Break Management**: Integrated lunch break scheduling
* **Activity Integration**: Configurable activity periods
* **Saturday Options**: Configurable as Holiday/Half Day/Full Day

### 👩‍🏫 Teacher Management

* **Subject Allocation**: Assign multiple subjects per teacher
* **Grade Assignment**: Flexible grade-level teaching assignments
* **Workload Distribution**: Automated and balanced scheduling
* **Schedule Tracking**: Individual teacher timetable generation

---

## 🚀 Getting Started

### Prerequisites

<details>
<summary>Click to expand</summary>

* Python 3.8 or higher
* Required Python packages:

  ```bash
  pip install pandas gradio
  ```

</details>

---

## 🔧 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/school-timetable-generator.git
   cd school-timetable-generator
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

1. Run the application:

   ```bash
   python Timetable.py
   ```

2. Access the web interface through your browser (the URL will be displayed in the terminal).

3. Follow these steps in the UI:

   * Add teachers with their subjects and grade levels
   * Configure time slots and schedule preferences
   * Generate timetables
   * Export or preview the generated schedules

---

## 📊 Output Format

The generator creates two types of CSV files in the `timetables` directory:

* **Class-wise timetables** (e.g., `Grade_1_A.csv`)
* **Teacher-wise schedules** (e.g., `Teacher_John_Doe.csv`)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

* Built with [Gradio](https://gradio.app/) for the user interface
* Uses [Pandas](https://pandas.pydata.org/) for data handling
* Follows NCERT curriculum guidelines
* Made with ❤️ for Indian Schools

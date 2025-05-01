from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
import random
import pandas as pd
import gradio as gr
import os
import tempfile
import re

@dataclass
class Teacher:
    name: str
    subjects: Set[str]
    grades: Set[str]
    schedule: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def initialize_schedule(self, days: List[str], time_slots: List[str]):
        self.schedule = {day: {slot: "" for slot in time_slots} for day in days}

    def is_available(self, day: str, time_slot: str) -> bool:
        return not self.schedule.get(day, {}).get(time_slot)

    def assign(self, day: str, time_slot: str, class_name: str):
        if day in self.schedule and time_slot in self.schedule[day]:
            self.schedule[day][time_slot] = class_name

class TimetableManager:
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    SATURDAY_OPTIONS = ["Holiday", "Half Day", "Full Day"]
    AVAILABLE_SLOTS = [
        "7:00-7:50 AM", "8:00-8:50 AM", "9:00-9:50 AM", "10:00-10:50 AM", "11:00-11:50 AM",
        "12:00-12:50 PM", "1:00-1:50 PM", "2:00-2:50 PM", "3:00-3:50 PM", "4:00-4:50 PM"
    ]
    ACTIVITY_SUBJECTS = ["Sports", "Drawing/Craft", "Drama", "Music", "Instrument", "Dance"]
    SECTIONS = ["A", "B", "C", "D", "E", "F", "G", "H"]
    GRADES = ["1-5", "6-8", "9-10", "11-12 Science", "11-12 Commerce", "11-12 Arts"]
    
    GRADE_MAPPING = {str(i): "1-5" for i in range(1, 6)} | {str(i): "6-8" for i in range(6, 9)} | \
                    {str(i): "9-10" for i in range(9, 11)} | {str(i): "11-12 Science" for i in range(11, 13)}

    NCERT_SUBJECTS = {
        "1-5": ["English", "Hindi", "Mathematics", "EVS", "Art", "Physical Education"],
        "6-8": ["English", "Hindi", "Mathematics", "Science", "Social Science", "Sanskrit", "Computer Basics"],
        "9-10": ["English", "Hindi", "Mathematics", "Science", "Social Science", "IT", "Commerce Basics"],
        "11-12 Science": ["Physics", "Chemistry", "Biology/Math", "Computer Science"],
        "11-12 Commerce": ["Accountancy", "Business Studies", "Economics"],
        "11-12 Arts": ["History", "Political Science", "Sociology"]
    }

    def __init__(self):
        self.teachers: Dict[str, Teacher] = {}
        self.subject_grade_teachers: Dict[Tuple[str, str], List[str]] = {}
        self.timetable_cache: Dict[str, pd.DataFrame] = {}
        self.teacher_timetable: Dict[str, pd.DataFrame] = {}
        self.output_dir = "timetables"
        os.makedirs(self.output_dir, exist_ok=True)

    def add_teacher(self, name: str, subjects_text: str, grades: List[str]) -> str:
        if not name or not subjects_text or not grades:
            return "❌ All fields are required!"
        subjects = {s.strip() for s in subjects_text.split(",") if s.strip()}
        grades_set = set(grades)
        self.teachers[name] = Teacher(name, subjects, grades_set)
        for subject in subjects:
            for grade in grades_set:
                key = (subject, grade)
                if key not in self.subject_grade_teachers:
                    self.subject_grade_teachers[key] = []
                self.subject_grade_teachers[key].append(name)
        return f"✅ Teacher {name} added successfully!"

    def list_teachers(self) -> str:
        if not self.teachers:
            return "<div class='empty-state'><h3>📋 No teachers added yet</h3><p>Add teachers to see them listed here.</p></div>"
        teachers_html = "<div class='teachers-list'><h3>👨‍🏫 Current Teachers</h3><div class='teacher-cards'>"
        for name, teacher in self.teachers.items():
            subjects_str = ", ".join(sorted(teacher.subjects))
            grades_str = ", ".join(sorted(teacher.grades))
            teachers_html += f"""
            <div class='teacher-card'>
                <div class='teacher-name'>{name}</div>
                <div class='teacher-details'>
                    <div class='detail-item'><span class='detail-label'>Subjects:</span> {subjects_str}</div>
                    <div class='detail-item'><span class='detail-label'>Grades:</span> {grades_str}</div>
                </div>
            </div>
            """
        teachers_html += "</div></div>"
        return f"""
        <style>
            .teachers-list {{font-family: 'Inter', sans-serif; margin: 0; padding: 0;}}
            .teacher-cards {{display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin-top: 12px;}}
            .teacher-card {{background: linear-gradient(145deg, #ffffff, #f0f0f0); border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 4px solid #4B6BFD;}}
            .teacher-card:hover {{transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.12);}}
            .teacher-name {{font-size: 18px; font-weight: 600; color: #1a1a1a; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #eaeaea;}}
            .teacher-details {{display: flex; flex-direction: column; gap: 6px;}}
            .detail-item {{font-size: 14px; color: #555; line-height: 1.4;}}
            .detail-label {{font-weight: 500; color: #666;}}
            .empty-state {{text-align: center; padding: 40px 20px; color: #666; background-color: #f9f9f9; border-radius: 12px; border: 1px dashed #ccc;}}
            .empty-state h3 {{margin-bottom: 8px; color: #555;}}
            .empty-state p {{font-size: 14px;}}
        </style>
        {teachers_html}
        """

    def get_available_teachers(self, subject: str, grade_key: str, day: str, time_slot: str) -> List[str]:
        return [name for name in self.subject_grade_teachers.get((subject, grade_key), [])
                if self.teachers[name].is_available(day, time_slot)]

    def assign_teacher(self, subject: str, grade_key: str, day: str, time_slot: str, class_name: str) -> str:
        available_teachers = self.get_available_teachers(subject, grade_key, day, time_slot)
        if not available_teachers:
            return "TBD"
        teacher = random.choice(available_teachers)
        self.teachers[teacher].assign(day, time_slot, class_name)
        return teacher

    @staticmethod
    def get_grade_key(grade: str) -> str:
        return TimetableManager.GRADE_MAPPING.get(grade, "11-12 Science")

    def _create_time_slots(self, start_hour: int, end_hour: int, count: int) -> List[str]:
        def format_hour(h: int) -> str:
            if h == 0 or h == 24:
                return "12:00-12:50 AM"
            elif h == 12:
                return "12:00-12:50 PM"
            else:
                period = "AM" if h < 12 else "PM"
                h = h if h <= 12 else h - 12
                return f"{h}:00-{h}:50 {period}"
        slots = [format_hour(h) for h in range(start_hour, end_hour + 1)]
        return slots[:count]

    def generate_timetable(self, params: Dict) -> Tuple[str, List[str]]:
        try:
            def parse_time(time_str: str) -> int:
                hour = int(time_str.split(":")[0])
                if "PM" in time_str and hour != 12:
                    return hour + 12
                elif "AM" in time_str and hour == 12:
                    return 0
                return hour

            start_hour = parse_time(params['start_time'])
            end_hour = parse_time(params['end_time'])
            if end_hour <= start_hour:
                return "❌ End time must be after start time", []
            if end_hour - start_hour < int(params['periods_per_day']):
                return f"❌ Not enough hours ({end_hour - start_hour}) for {params['periods_per_day']} periods", []

            time_slots = self._create_time_slots(start_hour, end_hour, int(params['periods_per_day']))
            saturday_included = params['saturday_option'] != "Holiday"
            days = self.WEEKDAYS + (["Saturday"] if saturday_included else [])

            for teacher in self.teachers.values():
                teacher.initialize_schedule(days, time_slots)

            selected_sections = params['selected_sections'][:4]
            classes = [f"Grade {i} {section}" for i in range(1, 13) for section in selected_sections]
            if len(classes) != 48:
                return f"❌ Expected 48 classes (12 grades × 4 sections), got {len(classes)}. Adjust sections.", []

            self.timetable_cache.clear()
            self.teacher_timetable.clear()
            generated_files = []

            for class_name in classes:
                grade = class_name.split()[1]
                grade_key = self.get_grade_key(grade)
                timetable = {time: {day: "" for day in days} for time in time_slots}

                saturday_slots = time_slots[:len(time_slots)//2] if params['saturday_option'] == "Half Day" else time_slots
                available_slots = {day: list(time_slots if day != "Saturday" else saturday_slots) for day in days}

                if params['lunch_time'] in time_slots:
                    for day in days:
                        timetable[params['lunch_time']][day] = "Lunch Break 🍽"
                        if params['lunch_time'] in available_slots[day]:
                            available_slots[day].remove(params['lunch_time'])

                activity_count = min(int(params['activity_count']), len(days) * len(time_slots))
                activity_options = list(params['activity_subjects'])
                if activity_options and activity_count > 0:
                    all_slots = [(day, time) for day in days for time in available_slots[day]]
                    activity_slots = random.sample(all_slots, min(activity_count, len(all_slots)))
                    for day, time in activity_slots:
                        activity = random.choice(activity_options)
                        teacher = self.assign_teacher(activity, grade_key, day, time, class_name)
                        timetable[time][day] = f"{activity} ({teacher})"
                        available_slots[day].remove(time)

                core_subjects = self.NCERT_SUBJECTS[grade_key]
                for day in days:
                    slots = available_slots[day]
                    for time in slots[:]:
                        subject = random.choice(core_subjects)
                        teacher = self.assign_teacher(subject, grade_key, day, time, class_name)
                        timetable[time][day] = f"{subject} ({teacher})"
                        slots.remove(time)

                df = pd.DataFrame.from_dict(timetable, orient='index', columns=days)
                filename = os.path.join(self.output_dir, f"{class_name.replace(' ', '_')}.csv")
                df.to_csv(filename, index_label="Time Slot")
                self.timetable_cache[class_name] = df
                generated_files.append(filename)

            teacher_schedules = {teacher: {day: {slot: t.schedule[day][slot] or "Free" 
                                                 for slot in time_slots} 
                                         for day in days} 
                                for teacher, t in self.teachers.items()}
            for teacher, schedule in teacher_schedules.items():
                df = pd.DataFrame.from_dict(schedule, orient='index', columns=days)
                filename = os.path.join(self.output_dir, f"Teacher_{teacher.replace(' ', '_')}.csv")
                df.to_csv(filename, index_label="Time Slot")
                self.teacher_timetable[teacher] = df
                generated_files.append(filename)

            return "✅ Generation Complete", generated_files

        except Exception as e:
            return f"❌ Error: {str(e)}", []

    def get_timetable_preview(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            # Convert the DataFrame to HTML table with styling
            html_table = df.to_html(classes='preview-table')
            return f"""
            <div class="timetable-preview">
                <h3>{os.path.basename(file_path).replace('_', ' ').replace('.csv', '')}</h3>
                {html_table}
            </div>
            """
        except Exception as e:
            return f"<div class='error'>Error loading preview: {str(e)}</div>"

def create_ui(manager: TimetableManager) -> gr.Blocks:
    timetable_theme = gr.themes.Soft(primary_hue="indigo", secondary_hue="blue", neutral_hue="slate")
    css = """
    .section-header {background: linear-gradient(90deg, #4F46E5, #3B82F6); border-radius: 8px; color: white; padding: 8px 16px; margin-bottom: 12px;}
    .section-header-icon {font-size: 20px; margin-right: 8px;}
    .card {background: white; border-radius: 12px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 16px;}
    
    /* Loading Animation */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        backdrop-filter: blur(5px);
    }
    
    .loading-spinner {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 8px solid transparent;
        border-top-color: #4F46E5;
        border-bottom-color: #3B82F6;
        animation: spin 1.5s linear infinite;
        position: relative;
    }
    
    .loading-spinner:before, .loading-spinner:after {
        content: '';
        position: absolute;
        border-radius: 50%;
    }
    
    .loading-spinner:before {
        top: 5px;
        left: 5px;
        right: 5px;
        bottom: 5px;
        border: 6px solid transparent;
        border-top-color: #818CF8;
        border-bottom-color: #60A5FA;
        animation: spin 1s linear infinite reverse;
    }
    
    .loading-text {
        position: absolute;
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: 600;
        margin-top: 140px;
    }
    
    .loading-progress {
        position: absolute;
        text-align: center;
        color: white;
        font-size: 14px;
        margin-top: 170px;
        opacity: 0.8;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Timetable Grid */
    .timetable-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
        margin-top: 20px;
    }
    
    .timetable-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        position: relative;
    }
    
    .timetable-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    
    .timetable-header {
        background: linear-gradient(45deg, #4F46E5, #60A5FA);
        color: white;
        padding: 12px 16px;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .timetable-icon {
        font-size: 18px;
        margin-right: 8px;
    }
    
    .timetable-content {
        padding: 12px 16px;
        color: #4B5563;
    }
    
    .timetable-teacher {
        background: linear-gradient(45deg, #10B981, #34D399);
    }
    
    .timetable-button {
        background-color: #4F46E5;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s;
    }
    
    .timetable-button:hover {
        background-color: #4338CA;
    }
    
    /* Preview Modal */
    .preview-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0,0,0,0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .preview-container {
        background: white;
        border-radius: 12px;
        width: 90%;
        max-width: 1200px;
        max-height: 90vh;
        overflow-y: auto;
        position: relative;
    }
    
    .preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .preview-title {
        font-size: 18px;
        font-weight: 600;
        color: #1F2937;
    }
    
    .preview-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6B7280;
    }
    
    .preview-content {
        padding: 20px;
    }
    
    .preview-actions {
        display: flex;
        justify-content: flex-end;
        padding: 16px 20px;
        border-top: 1px solid #e5e7eb;
        gap: 12px;
    }
    
    .preview-button {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        cursor: pointer;
    }
    
    .download-button {
        background-color: #4F46E5;
        color: white;
        border: none;
    }
    
    .download-button:hover {
        background-color: #4338CA;
    }
    
    /* Table Styling */
    .preview-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
        font-size: 14px;
    }
    
    .preview-table th, .preview-table td {
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
        text-align: left;
    }
    
    .preview-table th {
        background-color: #f3f4f6;
        font-weight: 600;
    }
    
    .preview-table tr:nth-child(even) {
        background-color: #f9fafb;
    }
    
    /* Pills for different subjects */
    .subject-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .timetable-grid {
            grid-template-columns: 1fr;
        }
        
        .preview-container {
            width: 95%;
            max-height: 95vh;
        }
    }
    
    /* Chat feature */
    .chat-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        z-index: 1000;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        max-height: 500px;
    }
    
    .chat-header {
        background: linear-gradient(90deg, #4F46E5, #3B82F6);
        color: white;
        padding: 12px 16px;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        font-size: 18px;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        max-height: 400px;
    }
    
    .chat-input-container {
        padding: 12px;
        border-top: 1px solid #e5e7eb;
        display: flex;
        gap: 8px;
    }
    
    .chat-input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #d1d5db;
        border-radius: 20px;
        outline: none;
    }
    
    .chat-send {
        background-color: #4F46E5;
        color: white;
        border: none;
        border-radius: 20px;
        width: 40px;
        cursor: pointer;
    }
    
    .message {
        padding: 8px 12px;
        border-radius: 18px;
        max-width: 80%;
        word-break: break-word;
    }
    
    .user-message {
        background-color: #4F46E5;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 4px;
    }
    
    .bot-message {
        background-color: #f3f4f6;
        color: #1F2937;
        align-self: flex-start;
        border-bottom-left-radius: 4px;
    }
    
    .chat-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #4F46E5, #3B82F6);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1001;
        color: white;
        font-size: 24px;
    }
    """

    with gr.Blocks(theme=timetable_theme, css=css) as app:
        # State variables
        generated_files_state = gr.State(value=[])
        selected_file_state = gr.State(value=None)
        is_chat_open = gr.State(value=False)

        with gr.Tabs() as tabs:
            with gr.TabItem("👨‍🏫 Teacher Management", id="teacher_management"):
                gr.HTML("""<div class="section-header"><span class="section-header-icon">👨‍🏫</span>Teacher Management</div>""")
                with gr.Row():
                    with gr.Column():
                        with gr.Group():
                            gr.HTML("""<h4 style="margin-top: 0; color: #4B5563;">Add New Teacher</h4>""")
                            name_input = gr.Textbox(label="Teacher Name", placeholder="Enter teacher's name")
                            subjects_input = gr.Textbox(label="Subjects (comma-separated)", placeholder="e.g., Mathematics, Physics")
                            grades_input = gr.Dropdown(manager.GRADES, label="Grade Levels", multiselect=True)
                            add_teacher_btn = gr.Button("Add Teacher", variant="primary")
                            result_text = gr.HTML()
                    with gr.Column():
                        teachers_list = gr.HTML()
                        refresh_btn = gr.Button("🔄 Refresh List")
                add_teacher_btn.click(fn=manager.add_teacher, inputs=[name_input, subjects_input, grades_input], outputs=[result_text]).then(fn=manager.list_teachers, outputs=[teachers_list])
                refresh_btn.click(fn=manager.list_teachers, outputs=[teachers_list])

            with gr.TabItem("📅 Generate Timetable", id="generate_timetable"):
                gr.HTML("""<div class="section-header"><span class="section-header-icon">📅</span>Generate Timetable</div>""")
                with gr.Row():
                    with gr.Column():
                        gr.HTML("""<h4 style="margin-top: 0; color: #4B5563;">Class Selection</h4>""")
                        sections_input = gr.Dropdown(manager.SECTIONS, label="Sections", multiselect=True, value=["A", "B", "C", "D"])
                    with gr.Column():
                        gr.HTML("""<h4 style="margin-top: 0; color: #4B5563;">Activity Options</h4>""")
                        activity_subjects_input = gr.Dropdown(manager.ACTIVITY_SUBJECTS, label="Activity Subjects", multiselect=True, value=["Sports"])
                        activity_count_input = gr.Dropdown(choices=["1", "2", "3"], label="Activities per Week", value="1")
                with gr.Row():
                    with gr.Column():
                        gr.HTML("""<h4 style="margin-top: 0; color: #4B5563;">Time Settings</h4>""")
                        start_time_input = gr.Dropdown(manager.AVAILABLE_SLOTS, label="Start Time", value="8:00-8:50 AM")
                        end_time_input = gr.Dropdown(manager.AVAILABLE_SLOTS, label="End Time", value="3:00-3:50 PM")
                        periods_input = gr.Slider(minimum=1, maximum=10, value=7, step=1, label="Periods per Day")
                        lunch_time_input = gr.Dropdown(manager.AVAILABLE_SLOTS, label="Lunch Time", value="12:00-12:50 PM")
                        saturday_option_input = gr.Radio(manager.SATURDAY_OPTIONS, label="Saturday Schedule", value="Half Day")
                generate_btn = gr.Button("Generate Timetables", variant="primary")
                status_text = gr.HTML()

            with gr.TabItem("📊 Timetable Results", id="timetable_results"):
                gr.HTML("""<div class="section-header"><span class="section-header-icon">📊</span>Timetable Results</div>""")
                timetable_list = gr.HTML(label="Generated Timetables")
                with gr.Row(visible=False) as preview_row:
                    preview_html = gr.HTML(label="Timetable Preview")
                    with gr.Column():
                        filename_text = gr.Text(label="Selected File")
                        download_btn = gr.Button("📥 Download", variant="primary")
                        back_btn = gr.Button("◀️ Back to List")

        # Loading overlay (hidden by default)
        loading_overlay = gr.HTML(
            value="""
            <div class="loading-overlay" id="loading-overlay" style="display: none;">
                <div class="loading-spinner"></div>
                <div class="loading-text">Generating Timetables</div>
                <div class="loading-progress">This may take a few moments...</div>
            </div>
            """,
            visible=False
        )
        
        # Chat feature
        chat_toggle = gr.HTML(
            value="""
            <div class="chat-toggle" id="chat-toggle" onclick="toggleChat()">
                💬
            </div>
            <div class="chat-container" id="chat-container" style="display: none;">
              <div class="chat-header">
                <span>Timetable Assistant</span>
                <button class="chat-close" onclick="toggleChat()">×</button>
              </div>
              <div class="chat-messages" id="chat-messages">
                <div class="message bot-message">
                  Hello! I'm your timetable assistant. How can I help you today?
                </div>
              </div>
              <div class="chat-input-container">
                <input type="text" id="chat-input" placeholder="Type your message..." />
                <button class="chat-send" id="chat-send">Send</button>
              </div>
            </div>
            """,
            visible=True
        )
        
        # JavaScript for chat toggle and other interactive features
        app.load(None, js="""
        function toggleChat() {
            const chatContainer = document.getElementById('chat-container');
            const isVisible = chatContainer.style.display !== 'none';
            chatContainer.style.display = isVisible ? 'none' : 'flex';
        }
        
        function showLoading() {
            document.getElementById('loading-overlay').style.display = 'flex';
        }
        
        function hideLoading() {
            document.getElementById('loading-overlay').style.display = 'none';
        }
        
        // Initialize chat functionality
        document.addEventListener('DOMContentLoaded', function() {
            const chatInput = document.getElementById('chat-input');
            const chatSend = document.getElementById('chat-send');
            const chatMessages = document.getElementById('chat-messages');
            
            function sendMessage() {
                const message = chatInput.value.trim();
                if (message) {
                    // Add user message
                    const userMsg = document.createElement('div');
                    userMsg.className = 'message user-message';
                    userMsg.textContent = message;
                    chatMessages.appendChild(userMsg);
                    
                    // Clear input
                    chatInput.value = '';
                    
                    // Scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    
                    // Simulate bot response (in a real app, this would call an API)
                    setTimeout(() => {
                        const botMsg = document.createElement('div');
                        botMsg.className = 'message bot-message';
                        botMsg.textContent = 'I\'m sorry, I\'m just a demo assistant. The full version would provide helpful responses about timetable generation.';
                        chatMessages.appendChild(botMsg);
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }, 1000);
                }
            }
            
            if (chatSend) {
                chatSend.addEventListener('click', sendMessage);
            }
            
            if (chatInput) {
                chatInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            }
        });
        """)
        
        # Event handlers
        def update_timetable_list():
            if not os.path.exists(manager.output_dir) or not os.listdir(manager.output_dir):
                return "<div class='empty-state'><h3>📋 No timetables generated yet</h3><p>Go to the 'Generate Timetable' tab to create timetables.</p></div>"
            
            files = [f for f in os.listdir(manager.output_dir) if f.endswith('.csv')]
            class_files = [f for f in files if not f.startswith('Teacher_')]
            teacher_files = [f for f in files if f.startswith('Teacher_')]
            
            # Sort class files by grade number
            def get_grade_number(filename):
                # Extract grade number from filename (e.g., 'Grade_10_A.csv' -> 10)
                match = re.search(r'Grade_(\d+)_', filename)
                if match:
                    return int(match.group(1))
                return 999  # Return a high number for files that don't match the pattern
                
            class_files.sort(key=get_grade_number)
            
            html = "<div class='timetable-grid'>"
            
            # Class timetables
            for file in class_files:
                class_name = file.replace('_', ' ').replace('.csv', '')
                html += f"""
                <div class='timetable-card' onclick="selectTimetable('{file}')">
                    <div class='timetable-header'>
                        <span><span class='timetable-icon'>📚</span>{class_name}</span>
                    </div>
                    <div class='timetable-content'>
                        <p>Class schedule for {class_name}</p>
                        <button class='timetable-button' onclick="event.stopPropagation(); viewTimetable('{file}')">View</button>
                    </div>
                </div>
                """
            
            # Teacher timetables
            for file in teacher_files:
                teacher_name = file.replace('Teacher_', '').replace('_', ' ').replace('.csv', '')
                html += f"""
                <div class='timetable-card'>
                    <div class='timetable-header timetable-teacher'>
                        <span><span class='timetable-icon'>👨‍🏫</span>{teacher_name}</span>
                    </div>
                    <div class='timetable-content'>
                        <p>Teaching schedule</p>
                        <button class='timetable-button' onclick="event.stopPropagation(); viewTimetable('{file}')">View</button>
                    </div>
                </div>
                """
            
            html += "</div>"
            
            # Add JavaScript for timetable selection
            html += """
            <script>
            function selectTimetable(filename) {
                const event = new CustomEvent('timetable-selected', { detail: filename });
                document.dispatchEvent(event);
            }
            
            function viewTimetable(filename) {
                const event = new CustomEvent('timetable-view', { detail: filename });
                document.dispatchEvent(event);
            }
            </script>
            """
            
            return html
        
        def generate_timetables(sections, activity_subjects, activity_count, start_time, end_time, periods, lunch_time, saturday_option):
            # Show loading overlay
            loading_overlay.visible = True
            yield loading_overlay, preview_row, status_text
            
            # Prepare parameters
            params = {
                'selected_sections': sections,
                'activity_subjects': activity_subjects,
                'activity_count': activity_count,
                'start_time': start_time,
                'end_time': end_time,
                'periods_per_day': periods,
                'lunch_time': lunch_time,
                'saturday_option': saturday_option
            }
            
            # Generate timetables
            status, files = manager.generate_timetable(params)
            
            # Hide loading overlay
            loading_overlay.visible = False
            preview_row.visible = False
            
            # Update UI
            timetable_list = update_timetable_list()
            return loading_overlay, preview_row, status, timetable_list
        
        def show_preview(file_path):
            if not file_path or not os.path.exists(os.path.join(manager.output_dir, file_path)):
                return "<div class='error'>File not found</div>", file_path, gr.update(visible=True)
            
            full_path = os.path.join(manager.output_dir, file_path)
            preview_html = manager.get_timetable_preview(full_path)
            return preview_html, file_path, gr.update(visible=True)
        
        def download_file(file_path):
            if not file_path or not os.path.exists(os.path.join(manager.output_dir, file_path)):
                return None
            
            return os.path.join(manager.output_dir, file_path)
        
        # Connect event handlers
        # Using a proper approach for tab changes instead of using tabs as input
        with gr.Blocks() as tab_change_handler:
            tab_select = gr.Textbox(visible=False)
            tab_select.change(lambda tab: update_timetable_list() if tab == "timetable_results" else None, inputs=tab_select, outputs=timetable_list)
        
        # Use JavaScript to handle tab changes and update the hidden textbox
        app.load(None, js="""
        function setupTabChangeListener() {
            const tabButtons = document.querySelectorAll('.tabitem');
            const tabSelect = document.getElementById('tab_select');
            
            if (tabButtons && tabSelect) {
                tabButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        // Get the tab ID from the button's data attribute or class
                        const tabId = this.getAttribute('data-tab') || this.textContent.trim();
                        // Update the hidden textbox with the tab ID
                        tabSelect.value = tabId;
                        // Trigger the change event
                        const event = new Event('input', { bubbles: true });
                        tabSelect.dispatchEvent(event);
                    });
                });
            }
        }
        
        // Run after the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', setupTabChangeListener);
        // Also run when Gradio refreshes the UI
        document.addEventListener('gradio-loaded', setupTabChangeListener);
        """)
        
        generate_btn.click(
            fn=generate_timetables,
            inputs=[sections_input, activity_subjects_input, activity_count_input, 
                   start_time_input, end_time_input, periods_input, 
                   lunch_time_input, saturday_option_input],
            outputs=[loading_overlay, preview_row, status_text, timetable_list]
        )
        
        # Switch to results tab after generation
        generate_btn.click(
            fn=lambda: gr.update(selected=1),
            outputs=tabs,
            show_progress=False
        )
        
        # Custom event handling for timetable selection
        app.load(None, js="""
        document.addEventListener('timetable-selected', function(e) {
            const filename = e.detail;
            // Use gradio's function calling mechanism
            gradioApp().querySelector('#selected_file_state').value = filename;
            // Trigger preview update
            const viewButton = gradioApp().querySelector('#view_button');
            if (viewButton) viewButton.click();
        });
        
        document.addEventListener('timetable-view', function(e) {
            const filename = e.detail;
            // Use gradio's function calling mechanism
            gradioApp().querySelector('#selected_file_state').value = filename;
            // Trigger preview update
            const viewButton = gradioApp().querySelector('#view_button');
            if (viewButton) viewButton.click();
        });
        """)
        
        # Hidden button to trigger preview update
        view_button = gr.Button(elem_id="view_button", visible=False)
        view_button.click(fn=show_preview, inputs=[selected_file_state], outputs=[preview_html, filename_text, preview_row])
        
        # Back button functionality
        back_btn.click(fn=lambda: (gr.update(visible=False), update_timetable_list()), outputs=[preview_row, timetable_list])
        
        # Download button functionality
        download_btn.click(fn=download_file, inputs=[filename_text], outputs=[])
        
        # Initialize teachers list on load
        app.load(fn=manager.list_teachers, outputs=teachers_list)
        
        return app

# Main execution
if __name__ == "__main__":
    manager = TimetableManager()
    app = create_ui(manager)
    app.launch()
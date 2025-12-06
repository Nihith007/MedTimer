import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import turtle
from PIL import Image
import time

# Page configuration
st.set_page_config(
    page_title="MedTimer - Daily Medicine Companion",
    page_icon="💊",
    layout="wide"
)

# Initialize session state for medicines
if 'medicines' not in st.session_state:
    st.session_state.medicines = []
if 'adherence_data' not in st.session_state:
    st.session_state.adherence_data = {}

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .medicine-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
    }
    .taken-card {
        border-left-color: #4CAF50;
        background-color: #e8f5e9;
    }
    .upcoming-card {
        border-left-color: #ff9800;
        background-color: #fff3e0;
    }
    .missed-card {
        border-left-color: #f44336;
        background-color: #ffebee;
    }
    .adherence-score {
        font-size: 48px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
    }
    .score-label {
        text-align: center;
        color: #666;
        font-size: 14px;
    }
    .main-header {
        color: #2c3e50;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Turtle drawing functions
def draw_smiley():
    """Draw a smiley face using turtle"""
    buffer = BytesIO()
    
    # Create turtle screen
    screen = turtle.Screen()
    screen.bgcolor("#f8f9fa")
    screen.setup(300, 300)
    
    # Create turtle
    t = turtle.Turtle()
    t.speed(0)  # Fastest speed
    t.hideturtle()
    
    # Draw face
    t.penup()
    t.goto(0, -100)
    t.pendown()
    t.fillcolor("#FFD700")
    t.begin_fill()
    t.circle(100)
    t.end_fill()
    
    # Draw eyes
    t.penup()
    t.goto(-40, 40)
    t.pendown()
    t.fillcolor("white")
    t.begin_fill()
    t.circle(20)
    t.end_fill()
    
    t.penup()
    t.goto(40, 40)
    t.pendown()
    t.begin_fill()
    t.circle(20)
    t.end_fill()
    
    # Draw pupils
    t.penup()
    t.goto(-40, 50)
    t.pendown()
    t.fillcolor("black")
    t.begin_fill()
    t.circle(10)
    t.end_fill()
    
    t.penup()
    t.goto(40, 50)
    t.pendown()
    t.begin_fill()
    t.circle(10)
    t.end_fill()
    
    # Draw smile
    t.penup()
    t.goto(-50, -20)
    t.pendown()
    t.width(8)
    t.setheading(-60)
    t.circle(60, 120)
    
    # Save as PNG
    ts = t.getscreen()
    ts.getcanvas().postscript(file="temp_eps.ps")
    
    # Convert to PIL Image
    from PIL import Image
    img = Image.open("temp_eps.ps")
    
    # Save to buffer
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Clean up
    turtle.bye()
    
    return buffer

def draw_trophy():
    """Draw a trophy using turtle"""
    buffer = BytesIO()
    
    screen = turtle.Screen()
    screen.bgcolor("#f8f9fa")
    screen.setup(300, 300)
    
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    
    # Draw trophy base
    t.penup()
    t.goto(-40, -100)
    t.pendown()
    t.fillcolor("#FFD700")
    t.begin_fill()
    for _ in range(2):
        t.forward(80)
        t.left(90)
        t.forward(20)
        t.left(90)
    t.end_fill()
    
    # Draw trophy cup
    t.penup()
    t.goto(-30, -80)
    t.pendown()
    t.begin_fill()
    t.setheading(90)
    t.circle(30, 180)
    t.setheading(0)
    t.forward(60)
    t.setheading(270)
    t.circle(30, 180)
    t.end_fill()
    
    # Draw handles
    t.penup()
    t.goto(-50, -50)
    t.pendown()
    t.width(10)
    t.color("#FFD700")
    t.setheading(150)
    t.circle(20, 120)
    
    t.penup()
    t.goto(50, -50)
    t.pendown()
    t.setheading(30)
    t.circle(-20, 120)
    
    # Save as PNG
    ts = t.getscreen()
    ts.getcanvas().postscript(file="temp_eps.ps")
    
    img = Image.open("temp_eps.ps")
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    turtle.bye()
    
    return buffer

# Medicine management functions
def add_medicine(name, dosage, time_str, frequency, notes=""):
    medicine = {
        'id': len(st.session_state.medicines) + 1,
        'name': name,
        'dosage': dosage,
        'time': time_str,
        'frequency': frequency,
        'notes': notes,
        'taken': False,
        'date_added': date.today().isoformat()
    }
    st.session_state.medicines.append(medicine)
    
    # Update adherence data
    today = date.today().isoformat()
    if today not in st.session_state.adherence_data:
        st.session_state.adherence_data[today] = {'expected': 0, 'taken': 0}
    st.session_state.adherence_data[today]['expected'] += 1

def mark_as_taken(medicine_id):
    for med in st.session_state.medicines:
        if med['id'] == medicine_id:
            med['taken'] = True
            
            # Update adherence data
            today = date.today().isoformat()
            if today in st.session_state.adherence_data:
                st.session_state.adherence_data[today]['taken'] += 1
            break

def calculate_adherence_score():
    """Calculate adherence score for last 7 days"""
    if not st.session_state.adherence_data:
        return 0
    
    today = date.today()
    seven_days_ago = today - timedelta(days=6)
    
    total_expected = 0
    total_taken = 0
    
    for day_offset in range(7):
        current_day = today - timedelta(days=day_offset)
        day_str = current_day.isoformat()
        
        if day_str in st.session_state.adherence_data:
            data = st.session_state.adherence_data[day_str]
            total_expected += data['expected']
            total_taken += data['taken']
    
    if total_expected == 0:
        return 0
    
    return round((total_taken / total_expected) * 100)

# Streamlit UI
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/medicine.png", width=80)
        st.title("💊 MedTimer")
        st.subheader(f"{datetime.now().strftime('%A, %B %d')}")
        
        # Navigation
        page = st.radio("Navigate", ["🏠 Home", "➕ Add Medicine", "📊 Report", "⭐ Score"])
    
    # Home Page
    if page == "🏠 Home":
        st.title("Today's Medicines")
        
        if not st.session_state.medicines:
            st.info("No medicines added yet. Go to 'Add Medicine' to get started!")
        else:
            current_time = datetime.now().time()
            
            for med in st.session_state.medicines:
                med_time = datetime.strptime(med['time'], "%H:%M").time()
                
                # Determine status
                if med['taken']:
                    status_class = "taken-card"
                    status_text = "✓ Taken"
                    status_color = "#4CAF50"
                elif current_time >= med_time:
                    status_class = "missed-card"
                    status_text = "✗ Missed"
                    status_color = "#f44336"
                else:
                    status_class = "upcoming-card"
                    status_text = "⏰ Upcoming"
                    status_color = "#ff9800"
                
                # Display medicine card
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="medicine-card {status_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #2c3e50;">{med['name']}</h4>
                                <p style="margin: 5px 0; color: #666;">{med['dosage']} • {med['time']} - {med['frequency']}</p>
                                {f'<p style="margin: 5px 0; color: #666;"><em>{med["notes"]}</em></p>' if med['notes'] else ''}
                            </div>
                            <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if not med['taken'] and current_time < med_time:
                        if st.button("Mark Taken", key=f"mark_{med['id']}"):
                            mark_as_taken(med['id'])
                            st.rerun()
            
            st.markdown("---")
            st.subheader(f"Total Today: {len(st.session_state.medicines)}")
    
    # Add Medicine Page
    elif page == "➕ Add Medicine":
        st.title("Add Medicine")
        
        with st.form("add_medicine_form"):
            name = st.text_input("Medicine Name *", placeholder="e.g., Aspirin")
            dosage = st.text_input("Dosage *", placeholder="e.g., 100mg, 1 tablet")
            med_time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())
            frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Weekly", "As Needed"])
            notes = st.text_area("Notes (Optional)", placeholder="e.g., Take with food")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Add Medicine", type="primary")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submit:
                if name and dosage:
                    add_medicine(name, dosage, med_time.strftime("%H:%M"), frequency, notes)
                    st.success(f"✅ {name} added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    # Report Page
    elif page == "📊 Report":
        st.title("7-Day Report")
        st.markdown("Your medication history at a glance")
        
        # Generate report data
        today = date.today()
        dates = [(today - timedelta(days=i)).strftime("%a %d") for i in range(6, -1, -1)]
        
        # Create report table
        report_data = []
        for med in st.session_state.medicines:
            row = {"Medicine": f"{med['name']}\n{med['dosage']}"}
            for day_offset in range(6, -1, -1):
                current_day = today - timedelta(days=day_offset)
                day_str = current_day.strftime("%a %d")
                
                # Check if medicine should be taken on this day
                if current_day.isoformat() >= med['date_added']:
                    row[day_str] = "☑" if med['taken'] else "☒"
                else:
                    row[day_str] = ""
            
            report_data.append(row)
        
        if report_data:
            df = pd.DataFrame(report_data)
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="medtimer_report.csv" class="stButton">📥 Export to CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("No medicine history available.")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Medicines", len(st.session_state.medicines))
        with col2:
            days_tracked = len(st.session_state.adherence_data)
            st.metric("Days Tracked", days_tracked if days_tracked <= 7 else 7)
        with col3:
            total_taken = sum(data['taken'] for data in st.session_state.adherence_data.values())
            st.metric("Total Taken", total_taken)
        
        st.markdown("**Legend**")
        st.markdown("☑ Medicine taken • ☒ Medicine not taken")
    
    # Score Page
    else:
        st.title("Adherence Score")
        st.markdown("Your medication adherence over the last 7 days")
        
        score = calculate_adherence_score()
        
        # Display score with visual
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f'<div class="adherence-score">{score}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="score-label">Adherence</div>', unsafe_allow_html=True)
            
            # Draw turtle graphic based on score
            if score >= 80:
                st.markdown("### 🎉 Excellent!")
                buffer = draw_trophy()
                st.image(buffer, caption="High Adherence Trophy!")
            elif score >= 50:
                st.markdown("### 👍 Good Job!")
                buffer = draw_smiley()
                st.image(buffer, caption="Keep it up!")
            else:
                st.markdown("### 💪 Keep Trying!")
                st.info("Don't worry! Every day is a new chance to improve your routine.")
        
        with col2:
            # Display statistics
            st.subheader("7-Day Statistics")
            
            today = date.today()
            total_expected = 0
            total_taken = 0
            
            for day_offset in range(7):
                current_day = today - timedelta(days=day_offset)
                day_str = current_day.isoformat()
                
                if day_str in st.session_state.adherence_data:
                    data = st.session_state.adherence_data[day_str]
                    total_expected += data['expected']
                    total_taken += data['taken']
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Total Medicines", len(st.session_state.medicines))
            with col_stat2:
                st.metric("Doses Taken", total_taken)
            with col_stat3:
                st.metric("Expected Doses", total_expected)
            
            # Progress bar
            if total_expected > 0:
                progress = total_taken / total_expected
                st.progress(progress)
                st.caption(f"Progress: {total_taken}/{total_expected} doses")
            
            # Adherence trend chart
            if st.session_state.adherence_data:
                dates = []
                adherence_rates = []
                
                for day_offset in range(6, -1, -1):
                    current_day = today - timedelta(days=day_offset)
                    day_str = current_day.isoformat()
                    
                    if day_str in st.session_state.adherence_data:
                        data = st.session_state.adherence_data[day_str]
                        if data['expected'] > 0:
                            rate = (data['taken'] / data['expected']) * 100
                        else:
                            rate = 0
                    else:
                        rate = 0
                    
                    dates.append(current_day.strftime("%a"))
                    adherence_rates.append(rate)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(dates, adherence_rates, marker='o', linewidth=2, color='#4CAF50')
                ax.fill_between(dates, adherence_rates, alpha=0.2, color='#4CAF50')
                ax.set_ylim(0, 100)
                ax.set_ylabel('Adherence %')
                ax.set_title('Weekly Adherence Trend')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

if __name__ == "__main__":
    main()

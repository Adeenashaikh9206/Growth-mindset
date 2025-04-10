import streamlit as st
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import random
import matplotlib.pyplot as plt
import base64
from PIL import Image
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Growth Mindset Tracker",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# App header
def display_header():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://cdn.pixabay.com/photo/2017/03/19/20/19/ball-2157465_1280.png", width=150)
    with col2:
        st.title("Growth Mindset Tracker")
        st.markdown("**Transform your thinking, unlock your potential**")

# Initialize session state
def init_session_state():
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    if 'goals' not in st.session_state:
        st.session_state.goals = []
    if 'habits' not in st.session_state:
        st.session_state.habits = [
            {"name": "Daily Learning", "streak": 0, "last_completed": None},
            {"name": "Positive Affirmations", "streak": 0, "last_completed": None},
            {"name": "Challenge Comfort Zone", "streak": 0, "last_completed": None}
        ]
    if 'quote_index' not in st.session_state:
        st.session_state.quote_index = 0

# Growth mindset quotes
def get_quotes():
    return [
        {"quote": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
        {"quote": "It's not that I'm so smart, it's just that I stay with problems longer.", "author": "Albert Einstein"},
        {"quote": "Failure is simply the opportunity to begin again, this time more intelligently.", "author": "Henry Ford"},
        {"quote": "The mind is just like a muscle - the more you exercise it, the stronger it gets.", "author": "Jordan Peterson"},
        {"quote": "You don't have to be great to start, but you have to start to be great.", "author": "Zig Ziglar"},
        {"quote": "Challenges are what make life interesting. Overcoming them is what makes life meaningful.", "author": "Joshua J. Marine"},
        {"quote": "The more you challenge yourself, the more you grow.", "author": "Unknown"},
        {"quote": "Effort is what ignites that ability and turns it into accomplishment.", "author": "Carol Dweck"}
    ]

# Display a random quote
def display_quote():
    quotes = get_quotes()
    quote = quotes[st.session_state.quote_index]
    
    st.markdown(f"""
    <div class="quote-container">
        <p class="quote-text">"{quote['quote']}"</p>
        <p class="quote-author">— {quote['author']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Next Quote"):
        st.session_state.quote_index = (st.session_state.quote_index + 1) % len(quotes)
        st.experimental_rerun()

# Journal section
def journal_section():
    st.header("📔 Mindset Journal")
    
    with st.expander("Add New Journal Entry"):
        today = datetime.date.today()
        entry_date = st.date_input("Date", today)
        entry = st.text_area("Reflect on your growth today:", height=150)
        
        if st.button("Save Journal Entry"):
            if entry.strip():
                st.session_state.journal_entries.append({
                    "date": entry_date,
                    "entry": entry
                })
                st.success("Journal entry saved!")
            else:
                st.warning("Please write something in your journal entry.")
    
    if st.session_state.journal_entries:
        st.subheader("Your Journal Entries")
        entries_df = pd.DataFrame(st.session_state.journal_entries)
        entries_df = entries_df.sort_values(by="date", ascending=False)
        
        for idx, row in entries_df.iterrows():
            with st.container():
                st.markdown(f"**{row['date'].strftime('%B %d, %Y')}**")
                st.write(row['entry'])
                st.markdown("---")

# Goals section
def goals_section():
    st.header("🎯 Growth Goals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Add New Goal"):
            goal = st.text_input("Goal")
            target_date = st.date_input("Target Date", min_value=datetime.date.today())
            category = st.selectbox("Category", ["Learning", "Career", "Personal", "Health", "Relationships"])
            
            if st.button("Add Goal"):
                if goal.strip():
                    st.session_state.goals.append({
                        "goal": goal,
                        "target_date": target_date,
                        "category": category,
                        "created": datetime.date.today(),
                        "completed": False
                    })
                    st.success("Goal added!")
                else:
                    st.warning("Please enter a goal.")
    
    with col2:
        if st.session_state.goals:
            st.subheader("Your Goals")
            
            for idx, goal in enumerate(st.session_state.goals):
                if not goal['completed']:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{goal['goal']}**")
                            st.caption(f"Category: {goal['category']} | Target: {goal['target_date']}")
                        with col2:
                            if st.button("✓", key=f"complete_{idx}"):
                                st.session_state.goals[idx]['completed'] = True
                                st.experimental_rerun()
                        st.progress(calculate_goal_progress(goal))
                        st.markdown("---")

# Calculate goal progress
def calculate_goal_progress(goal):
    created = goal['created']
    target = goal['target_date']
    today = datetime.date.today()
    
    total_days = (target - created).days
    elapsed_days = (today - created).days
    
    if elapsed_days <= 0:
        return 0
    elif elapsed_days >= total_days:
        return 100
    else:
        return min(100, int((elapsed_days / total_days) * 100))

# Habits section
def habits_section():
    st.header("🔄 Daily Growth Habits")
    
    st.markdown("""
    Track your daily habits that foster a growth mindset. 
    Maintain your streaks to build consistency and resilience.
    """)
    
    if st.session_state.habits:
        cols = st.columns(len(st.session_state.habits))
        
        for idx, habit in enumerate(st.session_state.habits):
            with cols[idx]:
                st.markdown(f"**{habit['name']}**")
                st.markdown(f"🔥 Streak: {habit['streak']} days")
                
                if st.button(f"Complete {habit['name']}", key=f"habit_{idx}"):
                    update_habit_streak(idx)
                
                st.markdown("---")

# Update habit streak
def update_habit_streak(habit_idx):
    today = datetime.date.today()
    habit = st.session_state.habits[habit_idx]
    
    if habit['last_completed'] != today:
        if habit['last_completed'] is None or (today - habit['last_completed']).days == 1:
            habit['streak'] += 1
        elif (today - habit['last_completed']).days > 1:
            habit['streak'] = 1
        
        habit['last_completed'] = today
        st.experimental_rerun()

# Insights section
def insights_section():
    st.header("📈 Growth Insights")
    
    if st.session_state.journal_entries or st.session_state.goals:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.journal_entries:
                st.subheader("Journal Activity")
                entries_df = pd.DataFrame(st.session_state.journal_entries)
                entries_df['date'] = pd.to_datetime(entries_df['date'])
                entries_count = entries_df.groupby(entries_df['date'].dt.to_period("M")).size()
                
                fig, ax = plt.subplots()
                entries_count.plot(kind='bar', ax=ax, color='skyblue')
                plt.title("Journal Entries Per Month")
                plt.xlabel("Month")
                plt.ylabel("Number of Entries")
                st.pyplot(fig)
        
        with col2:
            if st.session_state.goals:
                st.subheader("Goals Progress")
                goals_df = pd.DataFrame(st.session_state.goals)
                completed = goals_df['completed'].sum()
                pending = len(goals_df) - completed
                
                fig, ax = plt.subplots()
                ax.pie([completed, pending], labels=['Completed', 'Pending'], autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
                ax.set_title("Goals Completion Status")
                st.pyplot(fig)
    else:
        st.info("Start journaling and setting goals to see insights here.")

# Resources section
def resources_section():
    st.header("📚 Growth Resources")
    
    st.markdown("""
    ### Recommended Books
    - *Mindset: The New Psychology of Success* by Carol Dweck
    - *Grit: The Power of Passion and Perseverance* by Angela Duckworth
    - *Atomic Habits* by James Clear
    - *The Growth Mindset Coach* by Annie Brock and Heather Hundley
    """)
    
    st.markdown("""
    ### TED Talks
    - [The power of believing that you can improve](https://www.ted.com/talks/carol_dweck_the_power_of_believing_that_you_can_improve) - Carol Dweck
    - [Grit: The power of passion and perseverance](https://www.ted.com/talks/angela_lee_duckworth_grit_the_power_of_passion_and_perseverance) - Angela Duckworth
    - [The puzzle of motivation](https://www.ted.com/talks/dan_pink_the_puzzle_of_motivation) - Dan Pink
    """)
    
    st.markdown("""
    ### Daily Practices
    1. **Embrace challenges** - Seek out one difficult task each day
    2. **Learn from criticism** - Ask for feedback and reflect on it
    3. **Celebrate effort** - Recognize the process, not just outcomes
    4. **Inspire others** - Share your growth journey with someone
    """)

# Main app function
def main():
    init_session_state()
    display_header()
    
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a section", 
                              ["Dashboard", "Mindset Journal", "Growth Goals", 
                               "Daily Habits", "Insights", "Resources"])
    
    display_quote()
    st.markdown("---")
    
    if app_mode == "Dashboard":
        st.subheader("Your Growth Mindset Dashboard")
        journal_section()
        goals_section()
        habits_section()
    elif app_mode == "Mindset Journal":
        journal_section()
    elif app_mode == "Growth Goals":
        goals_section()
    elif app_mode == "Daily Habits":
        habits_section()
    elif app_mode == "Insights":
        insights_section()
    elif app_mode == "Resources":
        resources_section()

if __name__ == "__main__":
    main()
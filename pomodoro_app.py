#Goal: Productivity App with Pomodoro Section, Note section, and a Youtube music player section. 

#Imports 
import streamlit as st
import base64
from ytmusicapi import YTMusic
from streamlit_autorefresh import st_autorefresh
from urllib.parse import urlparse, parse_qs
import streamlit.components.v1 as components

#Page Configuration
st.set_page_config(page_title="Pomodoro Comfy App", layout="wide")

#CSS

#Hides the main menu, footer, and header
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
#Makes the header transparent
top_bar_css = """
<style>
header[data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0); /* Fully transparent */
}
</style>
"""

#Makes the footer hidden
hide_footer = """
<style>
footer {visibility: hidden;}
footer:after {content:''; visibility:hidden;}
</style>
"""


st.markdown(hide_footer, unsafe_allow_html=True)
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown(top_bar_css, unsafe_allow_html=True)


#Injects custom css styling(Font to Pooppins, reduces top padding, defining styles for .main-header and.section-heading)

st.markdown("""
<style>

.block-container {
        padding-top: 1rem !important;
    }


    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }



    .main-header {
    font-size: 2rem;
        font-weight: 700;
        margin-top: 0;
        padding-top: 0;
        text-align: center;
        
    }

    .section-heading {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }

</style>
""", unsafe_allow_html=True)

#Defining Functions
def clear_text():
    st.session_state.note_text = ""

#Set background to a file image
def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

#Css functions
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
   st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)



set_bg_local("background.jpg")
local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')


#Header section
st.markdown('<div class="main-header">Welcome to Pomodoro Comfy!</div>', unsafe_allow_html=True)
st.subheader("This productivity app combines the pomodoro technique, sticky notes for studying, and a youtube music player to create a relaxing workspace.")


st.markdown("<br>", unsafe_allow_html=True)
st.divider()

#Layout 
pomodoro_col, spacer, notes_col,spacer2, video_col = st.columns([1, 0.1, 1.2,0.1, 1.3])
st.markdown("<br>", unsafe_allow_html=True)

#Pomodoro section
with pomodoro_col:

    st.markdown('<div class="section-heading">Pomodoro Timer</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div id='summary'></div>", unsafe_allow_html=True)

    #Setting up pomodoro settings
    pomodoro_timer = st.number_input(
        "**How long should each focused work session be? (minutes)**",
        min_value=1,
        value=25
    )


    pomodoro_break_timer = st.number_input(
        "**How long should each break be? (minutes)**",
        min_value=1,
        value=5
    )


    #Setting Up Alarm for Pomodoro

    alarm_sounds = {
    "Classic Alarm": "https://raw.githubusercontent.com/sduong07/pomodoro_app/main/alarm/classic_alarm.mp3",
    "Motivation Alarm": "https://raw.githubusercontent.com/sduong07/pomodoro_app/main/alarm/motivation_alarm.mp3",
    "Piano Alarm": "https://raw.githubusercontent.com/sduong07/pomodoro_app/main/alarm/piano_alarm.mp3",
    "Rain Alarm": "https://raw.githubusercontent.com/sduong07/pomodoro_app/main/alarm/rain_alarm.mp3",
    "Uplifting Alarm": "https://raw.githubusercontent.com/sduong07/pomodoro_app/main/alarm/uplifting_alarm.mp3",
}
    

    alarm_sound = st.selectbox(
        "**Select an alarm sound**",
        list(alarm_sounds.keys())

    )

    alarm_sound_url = alarm_sounds[alarm_sound]

    st.markdown("**Preview selected alarm:**")
    st.audio(alarm_sound_url)



    ALERT_DURATION = st.number_input(
        "**How long should the alarm play? (seconds)**",
        min_value=2,
        max_value=7, 
        value=5
    )



    st.markdown("<br>", unsafe_allow_html=True)

    #initialize session state
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False

    if "paused" not in st.session_state:
        st.session_state.paused = False

    if "t1" not in st.session_state:
        st.session_state.t1 = pomodoro_timer * 60

    if "t2" not in st.session_state:
        st.session_state.t2 = pomodoro_break_timer * 60

    if "phase" not in st.session_state:
        st.session_state.phase = "work"

    if "alert_timer" not in st.session_state:
        st.session_state.alert_timer = 0

    if "next_phase" not in st.session_state:
        st.session_state.next_phase = None


    #start button
    if st.button("Start Pomodoro Timer"):
        st.session_state.button_clicked = True
        st.session_state.paused = False
        st.session_state.phase = "work"
        st.session_state.t1 = pomodoro_timer * 60
        st.session_state.t2 = pomodoro_break_timer * 60
        st.session_state.alert_timer = 0

        components.html("""
        <script>
            window.parent.document
                .getElementById("summary")
                .scrollIntoView({behavior: "smooth"});
        </script>
        """, height=0)


    #pause/resume button
    if st.session_state.button_clicked and st.session_state.phase != "done":

        pause_label = "Resume" if st.session_state.paused else "Pause"

        if st.button(pause_label):
            st.session_state.paused = not st.session_state.paused

        st_autorefresh(interval=1000, key="timer_refresh")


        #pomodoro
        if st.session_state.phase == "work":

            mins, secs = divmod(st.session_state.t1, 60)
            st.title(f"Work: {mins:02d}:{secs:02d}")

            if not st.session_state.paused:
                if st.session_state.t1 > 0:
                    st.session_state.t1 -= 1
                else:
                    st.success("Work session complete!")
                    st.session_state.phase = "alert"
                    st.session_state.next_phase = "break"
                    st.session_state.alert_timer = ALERT_DURATION


        #alarm
        elif st.session_state.phase == "alert":

            st.audio(alarm_sound_url, autoplay=True)

            if not st.session_state.paused:
                if st.session_state.alert_timer > 0:
                    st.session_state.alert_timer -= 1
                else:
                    st.session_state.phase = st.session_state.next_phase

                if st.session_state.next_phase == "break":
                    st.session_state.t2 = pomodoro_break_timer * 60

                elif st.session_state.next_phase == "work":
                    st.session_state.t1 = pomodoro_timer * 60


        #break
        elif st.session_state.phase == "break":

            mins, secs = divmod(st.session_state.t2, 60)
            st.title(f"Break: {mins:02d}:{secs:02d}")

            if not st.session_state.paused:
                if st.session_state.t2 > 0:
                    st.session_state.t2 -= 1
                else:
                    st.error("Break time is over—back to work!")
                    
                    st.session_state.phase = "alert"
                    st.session_state.next_phase = "work"
                    st.session_state.alert_timer = ALERT_DURATION

#Notes section
with notes_col:
    st.markdown('<div class="section-heading">Study Notes & Tasks </div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    bg_color = st.color_picker("**Select a background colour**", "#feff9c")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
<style>
.stTextArea [data-baseweb=base-input] {{
   background-color: {bg_color} !important;
   -webkit-text-fill-color: black !important;
}}
</style>
""", unsafe_allow_html=True)

    if "study_notes" not in st.session_state:
        st.session_state["study_notes"] = ""

    if "note_text" not in st.session_state:
        st.session_state.note_text = ""


    notes = st.text_area( "**Write your study notes or tasks here**", value=st.session_state["study_notes"], height=200, key="note_text")

    st.button("Clear Text", on_click=clear_text)

    st.download_button(
            label="Download text",
            data=notes,
            file_name="message.txt",
            on_click="ignore",
            type="primary",
            icon=":material/download:",
    )

        
#Youtube Music Player Section
with video_col:  
    ytmusic = YTMusic()
    st.markdown('<div class="section-heading">YouTube Music Player</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    
    
    #Setting up youtube player with curated playlist
    with st.expander("**Here are some sample playlist and genres for studying**"):
        videos = {
            #Lo-Fi Beats
            "Lo-fi Jazz" : "https://www.youtube.com/watch?v=CBSlu_VMS9U",
            "Lo-fi Hip Hop": "https://www.youtube.com/watch?v=-FlxM_0S2lA",
            "Pokemon Lo-fi ": "https://www.youtube.com/watch?v=ceHXUTnOlDc",
            "Studio Ghibi Lo-fi ": "https://www.youtube.com/watch?v=AZals4U6Z_I",
            "Japanese Lo-fi ": "https://www.youtube.com/watch?v=mVycGYAPehY",

            #Piano
            "Classical Piano": "https://www.youtube.com/watch?v=WLWJy1eXX2c",
            "Video Game Piano": "https://www.youtube.com/watch?v=k0h_8svvr1I",
            "Anime Piano": "https://www.youtube.com/watch?v=HSOtku1j600",
            "K-Pop Piano": "https://www.youtube.com/watch?v=KFJ3gNMq6do",
            "Studio Ghibli Piano": "https://www.youtube.com/watch?v=l4WkvqGe_Ak",
            "Jazz Piano": "https://www.youtube.com/watch?v=MYPVQccHhAQ",

            #Ambience
            "Nature Ambience": "https://www.youtube.com/watch?v=ipf7ifVSeDU",
            "Nintendo Video Game Ambience": "https://www.youtube.com/watch?v=MAsudG24NVM",
            "Kingdom Hearts Ambience": "https://www.youtube.com/watch?v=hegvprK4TrM",
            "Animal Crossing Ambience": "https://www.youtube.com/watch?v=CBYSzErVczM",
            

            #Cafe
            "Rainy Jazz Cafe": "https://www.youtube.com/watch?v=NJuSStkIZBg", 
            "K-Pop Cafe": "https://www.youtube.com/watch?v=zZgW3zi039M"

        }

        genres = ['Lo-fi', 'Piano', 'Ambience', 'Cafe']


        selected_genre = st.selectbox("**Select a genre**:", genres)

        filtered_videos = {name: url for name, url in videos.items() if selected_genre.lower() in name.lower()}

        selected_video = st.selectbox(f"**Select a {selected_genre} playlist**:", list(filtered_videos.keys()))


        st.markdown("<br>", unsafe_allow_html=True)
        st.write("**Now Playing:**")
        st.video(filtered_videos[selected_video])

    

    st.write("**Or play your own music**")

    #Setting up user choosing their own video with link
    with st.expander("Play a YouTube video by link"):
        song_link = st.text_input("YouTube video link")
        parsed_url = urlparse(song_link)
        query_params = parse_qs(parsed_url.query)
        request_video_id = query_params.get("v", [None])[0]


        if song_link.strip():
            loop = st.checkbox("Repeat video", value=True, key=f"loop_video_{request_video_id}")

            
            embed_url = f"https://www.youtube.com/embed/{request_video_id}?autoplay=1&mute=1"
            if loop:
                embed_url += f"&loop=1&playlist={request_video_id}"

            st.markdown(
                f"""
                <iframe width="100%" height="400"
                    src="{embed_url}"
                    frameborder="0"
                    allow="autoplay; encrypted-media"
                    allowfullscreen
                ></iframe>
                """,
                unsafe_allow_html=True
            )

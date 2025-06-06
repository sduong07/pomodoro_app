import streamlit as st
import time
import base64
from ytmusicapi import YTMusic
import datetime
from streamlit_autorefresh import st_autorefresh
from urllib.parse import urlparse, parse_qs

# Set page config
st.set_page_config(page_title="Pomodoro Comfy App", layout="wide")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


ytmusic = YTMusic()

# Set page config
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



set_bg_local("background.jpg")


# Function to convert image to base64
def get_base64_of_bin_file(bin_file_path):
    with open(bin_file_path, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load your local image (make sure it's in the same directory or provide the full path)
img_path = "background.jpg"  # Change this to your image filename
img_base64 = get_base64_of_bin_file(img_path)

# Create the CSS to set the background image
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
"""

top_bar_css = """
<style>
header[data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0); /* Fully transparent */
}
</style>
"""

# Inject CSS
st.markdown(page_bg_img, unsafe_allow_html=True)
st.markdown(top_bar_css, unsafe_allow_html=True)


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
   st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

#---------------------------------#

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown("""
<style>

.block-container {
        padding-top: 1rem !important;
    }


    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }



    /* Main heading */
    .main-header {

    font-size: 2rem;
        font-weight: 700;
        margin-top: 0;
        padding-top: 0;
        text-align: center;
        
    }

    /* Section headings */
    .section-heading {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    /* Subtext/labels */
    .subtext {
        font-size: 1rem;
        font-weight: 400;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


#st.header("Welcome to the Pomodoro comfy app. This app combines a pomodoro timer, sticky notes for studying, and a youtube music player to create a relaxing workspace.")
st.markdown('<div class="main-header">Welcome to the Pomodoro comfy app. This app combines a pomodoro timer, sticky notes for studying, and a youtube music player to create a relaxing workspace.</div>', unsafe_allow_html=True)


pomodoro_col, spacer, notes_col,spacer2, video_col = st.columns([1, 0.1, 1.2,0.1, 1.3])
st.markdown("<br>", unsafe_allow_html=True)



#Customize Timer/Sessions?/Alarm when it ends?


with pomodoro_col:



    st.markdown('<div class="section-heading">Pomodoro Timer</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    st.write("Settings")

    pomodoro_timer = st.number_input("How long is the pomodoro?", value=25, placeholder="Type a number")
    pomodoro_break_timer = st.number_input("How long is the break?", value=5, placeholder="Type a number")
    #alarm_type = st.selectbox("Select the alarm type:", ("Birds", "Clock", "Video Game"), index=None)
    #alarm_sounds = {"Birds": "bird_alarm.mp3","Clock": "clock_alarm.mp3", "Video Game": "game_alarm.mp3" }



    # Initialize session state
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False
    if 't1' not in st.session_state:
        st.session_state.t1 = 60 * pomodoro_timer       
        #st.session_state.t1 = 1500  # 25 minutes
    if 't2' not in st.session_state:
        st.session_state.t2 = 60 * pomodoro_break_timer   
        #st.session_state.t2 = 300   # 5 minutes
    if 'phase' not in st.session_state:
        st.session_state.phase = "work"  # can be "work", "break", or "done"

    # Button to start the timer
    with col2:
        if st.button("Start pomodoro session"):
            st.session_state.button_clicked = True
            st.session_state.phase = "work"
            st.session_state.t1 = 60 * pomodoro_timer
            st.session_state.t2 = 60 * pomodoro_break_timer 
            

    # Refresh every second
    if st.session_state.button_clicked and st.session_state.phase != "done":
        count = st_autorefresh(interval=1000, key="timer_refresh")

        if st.session_state.phase == "work":
            mins, secs = divmod(st.session_state.t1, 60)
            st.header(f"⏳ Work: {mins:02d}:{secs:02d}")
            if st.session_state.t1 > 0:
                st.session_state.t1 -= 1
            else:
                st.success("🔔 25 minutes is over! Time for a break!")

                st.session_state.phase = "break"
                st.session_state.t2 = 60 * pomodoro_break_timer

        elif st.session_state.phase == "break":
            mins, secs = divmod(st.session_state.t2, 60)
            st.header(f"⏳ Break: {mins:02d}:{secs:02d}")
            if st.session_state.t2 > 0:
                st.session_state.t2 -= 1
            else:
                st.error("⏰ 5 minute break is over!")
                st.session_state.phase = "done"
                st.session_state.button_clicked = False
                st.session_state.t1 = 60 * pomodoro_timer
                st.session_state.t2 = 60 * pomodoro_break_timer


#add an another? save? 
with notes_col:
    st.markdown('<div class="section-heading">Study Notes or Tasks</div>', unsafe_allow_html=True)

    bg_color = st.color_picker("Select a background colour", "#feff9c")

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

    def clear_text():
        st.session_state.note_text = ""


    notes = st.text_area( "Write your notes or tasks here", value=st.session_state["study_notes"], height=300, key="note_text")

    st.button("Clear Text", on_click=clear_text)

    st.download_button(
            label="Download text",
            data=notes,
            file_name="message.txt",
            on_click="ignore",
            type="primary",
            icon=":material/download:",
    )


        
#
with video_col:
    st.markdown('<div class="section-heading">Youtube Music Player</div>', unsafe_allow_html=True)


    #video_id = "dQw4w9WgXcQ"  # replace with your video ID
    

    st.write("Curated music to boost focus during long study sessions")


        # Dictionary of video titles and their URLs or file paths
    videos = {
        "Lofi hip hop": "https://www.youtube.com/watch?v=-FlxM_0S2lA",
        "Video Game Piano": "https://www.youtube.com/watch?v=k0h_8svvr1I",

        "Anime piano": "https://www.youtube.com/watch?v=Ls0BwNdIptM",
        "Kpop piano": "https://www.youtube.com/watch?v=S8GpX3SAeig",
        "Studio ghibli piano": "https://www.youtube.com/watch?v=l4WkvqGe_Ak",

        "Pokemon Lofi ": "https://www.youtube.com/watch?v=ceHXUTnOlDc",
        "Studio ghibi Lofi ": "https://www.youtube.com/watch?v=AZals4U6Z_I",
        "Lofi beats": "https://www.youtube.com/watch?v=_Ns2Liu-8qg",
        "Kop": "https://www.youtube.com/watch?v=0DEH4qY27N4"


    }

    # Let user select a video
    selected_video = st.selectbox("Select a music genre:", list(videos.keys()))

    # Show the selected video
    st.write("Now Playing:")
    st.video(videos[selected_video])

    

    st.write("Or play your own music")

    with st.expander("Choose a youtube video"):
        song_link = st.text_input("Youtube link")
        parsed_url = urlparse(song_link)
        query_params = parse_qs(parsed_url.query)
        request_video_id = query_params.get("v", [None])[0]



        if song_link.strip():
            loop = st.checkbox("Repeat video", value=True, key=f"loop_video_{request_video_id}")

            # Construct embed URL with optional loop
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

            #st.video(song_link)


        
    
   #Step 1: User input
    with st.expander("Search for a song on youtube"):
        query = st.text_input("For Example: 'lofi chill'")

    if query:
        # Step 2: Perform search
        results = ytmusic.search(query, filter="songs")

        # Step 3: Show results and play on click
        for idx, song in enumerate(results[:10]):
            title = song["title"]
            artist = song["artists"][0]["name"]
            video_id = song["videoId"]

            with st.expander(f"{title} - {artist}"):
                st.write(f"▶️ {title} by {artist}")
                #st.video(f"https://www.youtube.com/watch?v={video_id}")

                loop2 = st.checkbox("Repeat video", value=True, key=f"loop_video_{video_id}")
                embed_url2 = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"
                if loop2:
                    embed_url2 += f"&loop=1&playlist={video_id}"

                st.markdown(
                    f"""
                    <iframe width="100%" height="400"
                        src="{embed_url2}"
                        frameborder="0"
                        allow="autoplay; encrypted-media"
                        allowfullscreen
                    ></iframe>
                    """,
                    unsafe_allow_html=True
                ) 







    


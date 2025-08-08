# app.py
# FLAMES animated game using Streamlit
# Run: streamlit run app.py

import streamlit as st
import time
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FLAMES Animated", layout="centered")

# -----------------------
# Helper functions
# -----------------------
def sanitize(name: str) -> str:
    """Lowercase and remove spaces. Keep only letters so we work cleanly."""
    return "".join([ch for ch in name.lower() if ch.isalpha()])

def build_display_html(chars, removed_flags):
    """Return an HTML string showing characters, striking out removed ones."""
    bits = []
    for ch, rem in zip(chars, removed_flags):
        if rem:
            bits.append(f"<span style='margin:6px; font-size:26px; font-family:monospace;'><s>{ch}</s></span>")
        else:
            bits.append(f"<span style='margin:6px; font-size:26px; font-family:monospace;'>{ch}</span>")
    return "<div>" + " ".join(bits) + "</div>"

def find_common_pairs(a_chars, b_chars):
    """
    Find pairs of indices (i,j) where a_chars[i] matches b_chars[j] (first available).
    Returns list of (i,j) in the order we find them.
    """
    removed_a = [False]*len(a_chars)
    removed_b = [False]*len(b_chars)
    pairs = []
    for i, ch in enumerate(a_chars):
        for j, ch2 in enumerate(b_chars):
            if not removed_b[j] and ch == ch2:
                removed_a[i] = True
                removed_b[j] = True
                pairs.append((i, j))
                break
    return pairs, removed_a, removed_b

def eliminate_flames_animation(count, flames_placeholder, caption_placeholder, delay=0.6):
    """
    Animate the elimination process on the FLAMES list
    with a visible number counting animation before removal.
    """
    flames = list("FLAMES")
    steps = []
    
    while len(flames) > 1:
        n = len(flames)
        index = (count - 1) % n  # index to remove
        
        # COUNTING ANIMATION
        for num in range(1, count + 1):
            # highlight the current letter in the count
            highlight_index = (num - 1) % n
            display = []
            for idx, ch in enumerate(flames):
                if idx == highlight_index:
                    display.append(f"<span style='color:red; font-weight:bold;'>{ch}</span>")
                else:
                    display.append(ch)
            
            flames_placeholder.markdown(
                "<div style='font-family:monospace; font-size:28px;'>" + " &nbsp; ".join(display) + "</div>",
                unsafe_allow_html=True
            )
            caption_placeholder.markdown(f"Counting... <b>{num}</b>", unsafe_allow_html=True)
            time.sleep(delay / 2)  # short delay for counting steps
        
        # REMOVE THE TARGET LETTER
        removed_char = flames.pop(index)
        steps.append(removed_char)
        caption_placeholder.markdown(f"Strike! Removed <b>{removed_char}</b> ", unsafe_allow_html=True)
        time.sleep(delay / 1.5)
        
        # rotate so counting starts from next position
        if len(flames) > 0:
            flames = flames[index:] + flames[:index]
    
    final = flames[0]
    return final, steps

def map_result(letter):
    mapping = {
        "F": ("Friends", "🥳", "Just buddies… or is that what you're telling everyone?"),
        "L": ("Love", "❤️", "Oooh — love is in the air!"),
        "A": ("Affection", "😊", "Warm fuzzy vibes incoming."),
        "M": ("Marriage", "💍", "Better start planning the guest list!"),
        "E": ("Enemies", "😈", "Mortal Kombat theme starts playing..."),
        "S": ("Siblings", "👯", "Sibling energy: eternal teasing.")
    }
    return mapping.get(letter, ("Unknown", "", ""))

# -----------------------
# UI layout
# -----------------------
st.title("🎲 FLAMES")
st.write("Type two names and watch FLAMES play out step-by-step. Totally unscientific, 100% nostalgic fun.")

with st.form("names_form"):
    col1, col2 = st.columns(2)
    with col1:
        name1 = st.text_input("First name", max_chars=50)
    with col2:
        name2 = st.text_input("Second name", max_chars=50)
    submitted = st.form_submit_button("Start FLAMES")

if submitted:
    # input validation
    s1 = sanitize(name1)
    s2 = sanitize(name2)
    if s1 == "" or s2 == "":
        st.error("Please enter two names containing letters (not empty).")
    else:
        # placeholders for animated UI
        st.markdown("### Step 1 — Crossing out common letters")
        name1_ph = st.empty()
        name2_ph = st.empty()
        caption_ph = st.empty()
        # prepare lists
        a_chars = list(s1)
        b_chars = list(s2)
        pairs, removed_a, removed_b = find_common_pairs(a_chars, b_chars)

        # show initial
        name1_ph.markdown(build_display_html(a_chars, [False]*len(a_chars)), unsafe_allow_html=True)
        name2_ph.markdown(build_display_html(b_chars, [False]*len(b_chars)), unsafe_allow_html=True)
        time.sleep(0.4)

        # animate crosses
        for i, j in pairs:
            caption_ph.markdown("Ouch! There goes a common letter!", unsafe_allow_html=True)
            removed_a[i] = True
            removed_b[j] = True
            name1_ph.markdown(build_display_html(a_chars, removed_a), unsafe_allow_html=True)
            name2_ph.markdown(build_display_html(b_chars, removed_b), unsafe_allow_html=True)
            time.sleep(0.5)

        # After crossing done
        remaining = sum(1 for x in removed_a if not x) + sum(1 for x in removed_b if not x)
        caption_ph.markdown(f"Remaining letters after crossing: <b>{remaining}</b>", unsafe_allow_html=True)
        time.sleep(0.6)

        # show logic explanation (crisp)
        with st.expander("How this works — short & crisp"):
            st.write("""
            1. We remove matching letters between the two names (each match removes one letter from each name).  
            2. Count the total of leftover letters (this is the number used for counting).  
            3. Start with the letters F L A M E S. Count up to the leftover number and **remove** that letter.  
            4. Continue counting from the next letter, always up to the leftover number, removing one letter each time until one remains.  
            5. The remaining letter gives the result: F=Friends, L=Love, A=Affection, M=Marriage, E=Enemies, S=Siblings.
            """)

        # Step 2 — FLAMES elimination animated
        st.markdown("### Step 2 — Eliminating FLAMES")
        flames_ph = st.empty()
        caption2_ph = st.empty()
        final_letter, elimination_steps = eliminate_flames_animation(remaining, flames_ph, caption2_ph, delay=0.7)

        # Map to result & show final
        title, emoji, one_liner = map_result(final_letter)
        st.markdown(f"<h1 style='text-align:center;'>{emoji} <span style='font-size:42px;'>{title}</span> {emoji}</h1>", unsafe_allow_html=True)
        st.write(f"**Why:** Final letter: **{final_letter}**")
        st.info(one_liner)

        # Save session to CSV
        try:
            df = pd.DataFrame([{
                "timestamp": datetime.now().isoformat(),
                "name1": name1.strip(),
                "name2": name2.strip(),
                "remaining_count": remaining,
                "result_letter": final_letter,
                "result_word": title
            }])
            csv_path = "flames_sessions.csv"
            df.to_csv(csv_path, mode="a", index=False, header=not st.file_uploader)
            st.success(f"Saved session to `{csv_path}`")
        except Exception as e:
            st.warning(f"Couldn't save CSV: {e}")

        # Play again button
        if st.button("Play Again 🔁"):
            st.experimental_rerun()

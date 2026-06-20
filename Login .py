# ============================================================
# LOGIN PAGE MODULE
#
# Women Safety Analytics System
# Login Page UI and Authentication Logic
# ============================================================

import streamlit as st
import auth


def validate_login(email, password):

    if not email:
        return False, "Enter Email Address"

    if not password:
        return False, "Enter Password"

    return True, "Valid"


def show_login_page():
    """
    Render Login Page
    """

    st.markdown("""
    <div class="welcome-card">
        <h2>👩‍🦰 Women Safety Analytics</h2>
        <p>Protecting Women from Safety Threats</p>
        <h3>🔐 Login</h3>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input(
        "Email Address"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Login"):

            valid, msg = validate_login(
                email,
                password
            )

            if valid:

                user = auth.login_user(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_name = user

                    st.session_state.page = "dashboard"

                    st.rerun()

                else:

                    st.error(
                        "Invalid Email or Password"
                    )

            else:

                st.warning(msg)

    with col2:

        if st.button("Register"):

            st.session_state.page = "register"

            st.rerun()

    st.markdown("---")

    st.info(
        "Use your registered account to access SOS Alerts, "
        "Location Tracking, Incident Reporting, and Safety Analytics."
  )

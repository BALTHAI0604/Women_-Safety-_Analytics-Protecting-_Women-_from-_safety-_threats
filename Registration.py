# ============================================================
# REGISTRATION PAGE MODULE
#
# Women Safety Analytics System
# User Registration Page
# ============================================================

import streamlit as st
import auth


def validate_registration(
    full_name,
    email,
    phone,
    password,
    confirm_password
):

    if not full_name:
        return False, "Enter Full Name"

    if not email:
        return False, "Enter Email Address"

    if not phone:
        return False, "Enter Phone Number"

    if not password:
        return False, "Enter Password"

    if not confirm_password:
        return False, "Confirm Your Password"

    if password != confirm_password:
        return False, "Passwords Do Not Match"

    if len(password) < 6:
        return False, "Password Must Be At Least 6 Characters"

    return True, "Valid"


def show_register_page():
    """
    Render Registration Page
    """

    st.markdown("""
    <div class="welcome-card">
        <h2>👩‍🦰 Women Safety Analytics</h2>
        <p>Protecting Women from Safety Threats</p>
        <h3>📝 User Registration</h3>
    </div>
    """, unsafe_allow_html=True)

    full_name = st.text_input(
        "Full Name"
    )

    email = st.text_input(
        "Email Address"
    )

    phone = st.text_input(
        "Phone Number"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Register"):

            valid, msg = validate_registration(
                full_name,
                email,
                phone,
                password,
                confirm_password
            )

            if valid:

                success = auth.register_user(
                    full_name,
                    email,
                    phone,
                    password
                )

                if success:

                    st.success(
                        "Registration Successful"
                    )

                    st.session_state.page = "login"

                    st.rerun()

                else:

                    st.error(
                        "Email Already Exists"
                    )

            else:

                st.warning(msg)

    with col2:

        if st.button("Back to Login"):

            st.session_state.page = "login"

            st.rerun()

    st.markdown("---")

    st.info(
        "Create an account to access SOS Alerts, "
        "Location Tracking, Emergency Contacts, "
        "Incident Reporting, and Safety Analytics."
  )

# ============================================================
# DASHBOARD PAGE MODULE
#
# Women Safety Analytics System
# User Dashboard
# ============================================================

import streamlit as st


def show_dashboard():

    st.markdown("""
    <div class="welcome-card">
        <h2>👩‍🦰 Women Safety Analytics</h2>
        <p>Protecting Women from Safety Threats</p>
    </div>
    """, unsafe_allow_html=True)

    st.success(
        f"Welcome, {st.session_state.get('user_name', 'User')}"
    )

    st.markdown("---")

    st.subheader("📋 Dashboard")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("🚨 SOS Alert"):
            st.session_state.page = "sos_alert"
            st.rerun()

        if st.button("📍 Location Tracking"):
            st.session_state.page = "location_tracking"
            st.rerun()

        if st.button("📞 Emergency Contacts"):
            st.session_state.page = "emergency_contacts"
            st.rerun()

    with col2:

        if st.button("📝 Incident Report"):
            st.session_state.page = "incident_report"
            st.rerun()

        if st.button("📊 Safety Analytics"):
            st.session_state.page = "analytics"
            st.rerun()

        if st.button("🔔 Notifications"):
            st.session_state.page = "notifications"
            st.rerun()

    st.markdown("---")

    st.subheader("📈 Safety Overview")

    st.info("Total SOS Alerts: 15")
    st.info("Incident Reports Submitted: 10")
    st.info("Emergency Contacts Added: 5")
    st.info("Notifications Received: 8")

    st.markdown("---")

    if st.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.page = "login"

        st.rerun()

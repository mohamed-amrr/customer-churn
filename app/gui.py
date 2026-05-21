import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime


st.set_page_config(
    page_title="Churn Predictor Pro",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .section-title {
        color: #c4b5fd;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 28px 0 8px 0;
        padding-left: 4px;
        border-left: 3px solid #7c3aed;
    }
    .result-churn {
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        border: 1px solid #f87171;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .result-stay {
        background: linear-gradient(135deg, #064e3b, #065f46);
        border: 1px solid #34d399;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .result-banner h1 { font-size: 2.2rem; margin: 0; }
    .result-banner p  { margin: 6px 0 0; color: #d1d5db; }
    .metric-box {
        background: rgba(124,58,237,0.2);
        border: 1px solid rgba(124,58,237,0.4);
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-box .value { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
    .metric-box .label { font-size: 0.78rem; color: #9ca3af; margin-top: 2px; }
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 36px;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button:hover { opacity: 0.88; }
    label { color: #c4b5fd !important; font-size: 0.86rem !important; }
</style>
""", unsafe_allow_html=True)


# ── In-memory state initialization ──────────────────────────────────────────

def init_state():
    if "customers" not in st.session_state:
        # list of dicts: {id, name, email, phone, created_at}
        st.session_state.customers = []
        st.session_state.customer_seq = 0

    if "predictions" not in st.session_state:
        # list of dicts matching old predictions table columns
        st.session_state.predictions = []
        st.session_state.prediction_seq = 0

    if "audit_log" not in st.session_state:
        # list of dicts: {id, prediction_id, action, actor, timestamp, note}
        st.session_state.audit_log = []
        st.session_state.audit_seq = 0

init_state()


# ── In-memory helpers ────────────────────────────────────────────────────────

def _next_id(key):
    st.session_state[key] += 1
    return st.session_state[key]


def _add_audit(prediction_id, action, note, actor="system"):
    st.session_state.audit_log.append({
        "id": _next_id("audit_seq"),
        "prediction_id": prediction_id,
        "action": action,
        "actor": actor,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": note,
    })


def save_prediction(churn_result, probability, http_status,
                    response_time, payload, api_response, customer_id=None):
    pred_id = _next_id("prediction_seq")
    st.session_state.predictions.append({
        "id": pred_id,
        "customer_id": customer_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "churn_result": int(churn_result),
        "probability": probability,
        "http_status": http_status,
        "response_time": response_time,
        "payload": json.dumps(payload),
        "api_response": json.dumps(api_response),
    })

    # Trigger: log every new prediction
    _add_audit(pred_id, "PREDICTION_CREATED",
               f"Result: {'Churn' if churn_result else 'Stay'}")

    # Trigger: flag high-risk
    if probability is not None and probability > 0.75:
        _add_audit(pred_id, "HIGH_RISK_FLAGGED",
                   f"Probability {round(probability * 100, 1)}% exceeded 75% threshold")

    return pred_id


def upsert_customer(name, email, phone):
    if not name:
        return None
    # If email given, check for existing customer
    if email:
        for c in st.session_state.customers:
            if c["email"] == email:
                return c["id"]
    cid = _next_id("customer_seq")
    st.session_state.customers.append({
        "id": cid,
        "name": name or None,
        "email": email or None,
        "phone": phone or None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    return cid


def fetch_all_customers():
    rows = sorted(st.session_state.customers,
                  key=lambda r: r["created_at"], reverse=True)
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["id", "name", "email", "phone", "created_at"])


def update_customer(customer_id, name, email, phone):
    for c in st.session_state.customers:
        if c["id"] == customer_id:
            c["name"] = name
            c["email"] = email
            c["phone"] = phone
            break


def delete_customer(customer_id):
    st.session_state.customers = [
        c for c in st.session_state.customers if c["id"] != customer_id
    ]


def _customer_name(customer_id):
    for c in st.session_state.customers:
        if c["id"] == customer_id:
            return c["name"]
    return "Anonymous"


def _customer_email(customer_id):
    for c in st.session_state.customers:
        if c["id"] == customer_id:
            return c["email"]
    return None


def fetch_churn_summary():
    rows = []
    for p in reversed(st.session_state.predictions):
        rows.append({
            "id": p["id"],
            "customer_name": _customer_name(p["customer_id"]) if p["customer_id"] else "Anonymous",
            "email": _customer_email(p["customer_id"]) if p["customer_id"] else None,
            "timestamp": p["timestamp"],
            "prediction": "Churn" if p["churn_result"] else "Stay",
            "probability_pct": round(p["probability"] * 100, 1) if p["probability"] is not None else None,
            "response_time": p["response_time"],
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["id", "customer_name", "email", "timestamp",
                 "prediction", "probability_pct", "response_time"])


def fetch_daily_stats():
    if not st.session_state.predictions:
        return pd.DataFrame()
    by_date = {}
    for p in st.session_state.predictions:
        d = p["timestamp"][:10]
        entry = by_date.setdefault(d, {"total": 0, "churn": 0, "probs": [], "times": []})
        entry["total"] += 1
        entry["churn"] += p["churn_result"]
        if p["probability"] is not None:
            entry["probs"].append(p["probability"])
        if p["response_time"] is not None:
            entry["times"].append(p["response_time"])
    rows = []
    for d, v in sorted(by_date.items(), reverse=True)[:30]:
        rows.append({
            "date": d,
            "total_predictions": v["total"],
            "total_churn": v["churn"],
            "total_stay": v["total"] - v["churn"],
            "avg_probability": round(sum(v["probs"]) / len(v["probs"]) * 100, 1) if v["probs"] else None,
            "avg_response_time": round(sum(v["times"]) / len(v["times"]), 3) if v["times"] else None,
        })
    return pd.DataFrame(rows)


def fetch_high_risk_customers():
    if not st.session_state.predictions:
        return pd.DataFrame()
    by_cust = {}
    for p in st.session_state.predictions:
        if p["probability"] is None or p["probability"] <= 0.5:
            continue
        cid = p["customer_id"]
        entry = by_cust.setdefault(cid, {
            "name": _customer_name(cid) if cid else "Anonymous",
            "email": _customer_email(cid) if cid else None,
            "total_predictions": 0,
            "churn_count": 0,
            "max_probability": 0.0,
        })
        entry["total_predictions"] += 1
        entry["churn_count"] += p["churn_result"]
        if p["probability"] > entry["max_probability"]:
            entry["max_probability"] = p["probability"]
    rows = [
        {**v, "max_probability": round(v["max_probability"] * 100, 1)}
        for v in by_cust.values()
        if v["churn_count"] > 0
    ]
    rows.sort(key=lambda r: r["max_probability"], reverse=True)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def fetch_overall_stats():
    preds = st.session_state.predictions
    if not preds:
        return {}
    total = len(preds)
    churned = sum(p["churn_result"] for p in preds)
    probs = [p["probability"] for p in preds if p["probability"] is not None]
    avg_prob = round(sum(probs) / len(probs) * 100, 1) if probs else 0.0
    return {"total": total, "churned": churned, "stayed": total - churned, "avg_prob": avg_prob}


def fetch_audit_log():
    rows = list(reversed(st.session_state.audit_log))[:200]
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["id", "prediction_id", "action", "actor", "timestamp", "note"])


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ API Settings")
    api_url = st.text_input("API Endpoint", value="http://churn_api:8000/predict")
    api_key = st.text_input("API Key (optional)", type="password")
    timeout = st.slider("Timeout (s)", 5, 60, 15)
    st.markdown("---")
    st.markdown("## 👤 Link Customer (optional)")
    cust_name  = st.text_input("Customer Name")
    cust_email = st.text_input("Customer Email")
    cust_phone = st.text_input("Customer Phone")
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.75rem;color:#6b7280;'>Churn Predictor Pro · v2.0 · In-Memory</p>",
        unsafe_allow_html=True,
    )


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_predict, tab_history, tab_customers, tab_reports, tab_audit = st.tabs([
    "🔮 Predict", "📜 History", "👥 Customers", "📊 Reports", "🔍 Audit Log"
])

# ── PREDICT ──────────────────────────────────────────────────────────────────

with tab_predict:
    st.markdown("# 📡 Churn Predictor Pro")
    st.markdown(
        "<p style='color:#9ca3af;margin-top:-10px;'>Fill in the profile and hit <b>Predict</b>. "
        "Every result is saved in memory for this session.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.form("prediction_form"):

        st.markdown("<div class='section-title'>👤 Demographics</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: gender         = st.selectbox("Gender", ["Male", "Female"])
        with c2: senior_citizen = st.selectbox("Senior Citizen", [0, 1],
                                               format_func=lambda x: "Yes" if x else "No")
        with c3: partner    = st.selectbox("Has Partner", ["Yes", "No"])
        with c4: dependents = st.selectbox("Has Dependents", ["Yes", "No"])

        st.markdown("<div class='section-title'>🗂️ Account Details</div>", unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        with c5: tenure   = st.number_input("Tenure (months)", 0, 120, 12, 1)
        with c6: contract = st.selectbox("Contract Type",
                                         ["Month-to-month", "One year", "Two year"])
        with c7: paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])

        payment_method = st.selectbox("Payment Method", [
            "Electronic check", "Mailed check",
            "Bank transfer (automatic)", "Credit card (automatic)",
        ])

        st.markdown("<div class='section-title'>📞 Phone Services</div>", unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1: phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        with p2:
            multiple_lines = st.selectbox("Multiple Lines",
                                          ["No phone service", "No", "Yes"],
                                          disabled=(phone_service == "No"))
        if phone_service == "No":
            multiple_lines = "No phone service"

        st.markdown("<div class='section-title'>🌐 Internet Services</div>", unsafe_allow_html=True)
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        no_internet      = internet_service == "No"
        inet_opts        = (["No internet service", "No", "Yes"]
                            if not no_internet else ["No internet service"])

        i1, i2, i3 = st.columns(3)
        with i1:
            online_security  = st.selectbox("Online Security",   inet_opts)
            streaming_tv     = st.selectbox("Streaming TV",      inet_opts)
        with i2:
            online_backup    = st.selectbox("Online Backup",     inet_opts)
            streaming_movies = st.selectbox("Streaming Movies",  inet_opts)
        with i3:
            device_protection = st.selectbox("Device Protection", inet_opts)
            tech_support      = st.selectbox("Tech Support",      inet_opts)

        if no_internet:
            online_security = online_backup = device_protection = "No internet service"
            tech_support = streaming_tv = streaming_movies = "No internet service"

        st.markdown("<div class='section-title'>💳 Charges</div>", unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)
        with ch1:
            monthly_charges = st.number_input("Monthly Charges ($)", 0.0, 500.0, 65.0, 0.5)
        with ch2:
            total_charges = st.number_input("Total Charges ($)", 0.0, 15000.0,
                                            float(monthly_charges * tenure), 1.0)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🔮  Predict Churn")

    if submitted:
        payload = {
            "gender": gender, "SeniorCitizen": senior_citizen,
            "Partner": partner, "Dependents": dependents, "tenure": tenure,
            "PhoneService": phone_service, "MultipleLines": multiple_lines,
            "InternetService": internet_service, "OnlineSecurity": online_security,
            "OnlineBackup": online_backup, "DeviceProtection": device_protection,
            "TechSupport": tech_support, "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies, "Contract": contract,
            "PaperlessBilling": paperless_billing, "PaymentMethod": payment_method,
            "MonthlyCharges": monthly_charges, "TotalCharges": total_charges,
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        st.markdown("---")
        with st.spinner("Calling API…"):
            try:
                resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
                resp.raise_for_status()
                result = resp.json()

                churn = (result.get("churn") or result.get("prediction")
                         or result.get("result"))
                prob  = (result.get("probability") or result.get("churn_probability")
                         or result.get("confidence"))
                msg   = result.get("message", "")

                is_churn = str(churn).lower() in ("true", "1", "yes", "churn") if churn is not None else False

                # Save customer + prediction in session state
                customer_id = None
                if cust_name or cust_email:
                    customer_id = upsert_customer(cust_name, cust_email, cust_phone)

                pred_id = save_prediction(
                    churn_result=is_churn, probability=prob,
                    http_status=resp.status_code,
                    response_time=resp.elapsed.total_seconds(),
                    payload=payload, api_response=result,
                    customer_id=customer_id,
                )

                # Result banner
                if churn is not None:
                    css_cls = "result-churn" if is_churn else "result-stay"
                    icon    = "🚨" if is_churn else "✅"
                    label   = "LIKELY TO CHURN" if is_churn else "LIKELY TO STAY"
                    st.markdown(
                        f"<div class='{css_cls} result-banner'>"
                        f"<h1>{icon} {label}</h1>"
                        f"<p>{msg}</p>"
                        f"<p style='font-size:0.78rem;color:#9ca3af;margin-top:8px;'>"
                        f"Saved as prediction #{pred_id}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                # Metrics row
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(
                        f"<div class='metric-box'>"
                        f"<div class='value'>{f'{prob:.1%}' if prob is not None else 'N/A'}</div>"
                        f"<div class='label'>Churn Probability</div></div>",
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f"<div class='metric-box'><div class='value'>{resp.status_code}</div>"
                        f"<div class='label'>HTTP Status</div></div>",
                        unsafe_allow_html=True,
                    )
                with m3:
                    st.markdown(
                        f"<div class='metric-box'>"
                        f"<div class='value'>{resp.elapsed.total_seconds():.2f}s</div>"
                        f"<div class='label'>Response Time</div></div>",
                        unsafe_allow_html=True,
                    )
                with m4:
                    st.markdown(
                        f"<div class='metric-box'><div class='value'>#{pred_id}</div>"
                        f"<div class='label'>Prediction ID</div></div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📦 Full API Response"):
                    st.json(result)
                with st.expander("📤 Payload Sent"):
                    st.json(payload)

            except requests.exceptions.ConnectionError:
                st.error(f"❌ Connection refused at `{api_url}`. Is the API server running?")
            except requests.exceptions.Timeout:
                st.error(f"⏱️ Request timed out after {timeout}s.")
            except requests.exceptions.HTTPError as e:
                st.error(f"🔴 HTTP {resp.status_code}: {e}")
                with st.expander("Response body"):
                    st.text(resp.text)
            except Exception as e:
                st.error(f"⚠️ Unexpected error: {e}")


# ── HISTORY ───────────────────────────────────────────────────────────────────

with tab_history:
    st.markdown("## 📜 Prediction History")
    st.caption("Reads from in-memory prediction store — raw payloads are hidden.")

    if st.button("🔄 Refresh", key="refresh_history"):
        st.rerun()

    df_hist = fetch_churn_summary()
    if df_hist.empty:
        st.info("No predictions yet. Run a prediction on the Predict tab.")
    else:
        def colour_prediction(val):
            if val == "Churn":
                return "background-color:#7f1d1d;color:#fca5a5;"
            return "background-color:#064e3b;color:#6ee7b7;"

        st.dataframe(
            df_hist.style.map(colour_prediction, subset=["prediction"]),
            use_container_width=True,
        )
        st.download_button(
            "⬇️ Export CSV",
            data=df_hist.to_csv(index=False),
            file_name=f"churn_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )


# ── CUSTOMERS ─────────────────────────────────────────────────────────────────

with tab_customers:
    st.markdown("## 👥 Customer Management")
    st.caption("Full **CREATE / READ / UPDATE / DELETE** on the in-memory customer store.")

    add_tab, edit_tab, view_tab = st.tabs(["➕ Add", "✏️ Edit / Delete", "📋 View All"])

    # CREATE
    with add_tab:
        with st.form("add_cust"):
            a1, a2, a3 = st.columns(3)
            with a1: n_name  = st.text_input("Full Name *")
            with a2: n_email = st.text_input("Email")
            with a3: n_phone = st.text_input("Phone")
            if st.form_submit_button("➕ Add Customer"):
                if not n_name:
                    st.warning("Name is required.")
                else:
                    cid = upsert_customer(n_name, n_email, n_phone)
                    st.success(f"✅ Saved — Customer ID #{cid}")

    with edit_tab:
        df_c = fetch_all_customers()
        if df_c.empty:
            st.info("No customers yet.")
        else:
            sel_id  = st.selectbox("Select Customer ID", df_c["id"].tolist())
            sel_row = df_c[df_c["id"] == sel_id].iloc[0]

            with st.form("edit_cust"):
                e1, e2, e3 = st.columns(3)
                with e1: u_name  = st.text_input("Name",  value=sel_row["name"]  or "")
                with e2: u_email = st.text_input("Email", value=sel_row["email"] or "")
                with e3: u_phone = st.text_input("Phone", value=sel_row["phone"] or "")
                col_upd, col_del = st.columns(2)
                with col_upd: do_upd = st.form_submit_button("💾 Save Changes")
                with col_del: do_del = st.form_submit_button("🗑️ Delete")

            if do_upd:
                update_customer(sel_id, u_name, u_email, u_phone)
                st.success(f"✅ Customer #{sel_id} updated.")
                st.rerun()
            if do_del:
                delete_customer(sel_id)
                st.warning(f"🗑️ Customer #{sel_id} deleted.")
                st.rerun()

    with view_tab:
        st.dataframe(fetch_all_customers(), use_container_width=True)


# ── REPORTS ───────────────────────────────────────────────────────────────────

with tab_reports:
    st.markdown("## 📊 Reports & Analytics")

    if st.button("🔄 Refresh", key="refresh_reports"):
        st.rerun()

    stats = fetch_overall_stats()
    if stats and stats.get("total", 0) > 0:
        k1, k2, k3, k4 = st.columns(4)
        for col, val, lbl in [
            (k1, stats["total"],   "Total Predictions"),
            (k2, stats["churned"], "Predicted Churn"),
            (k3, stats["stayed"],  "Predicted Stay"),
            (k4, f"{stats['avg_prob']}%", "Avg Probability"),
        ]:
            with col:
                st.markdown(
                    f"<div class='metric-box'><div class='value'>{val}</div>"
                    f"<div class='label'>{lbl}</div></div>",
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    st.markdown("### 📈 Daily Prediction Trend (last 30 days)")
    st.caption("Grouped by date with totals, churn count, and averages.")
    df_daily = fetch_daily_stats()
    if df_daily.empty:
        st.info("No data yet.")
    else:
        st.dataframe(df_daily, use_container_width=True)
        st.bar_chart(
            df_daily.set_index("date")[["total_predictions", "total_churn", "total_stay"]]
        )

    st.markdown("---")

    st.markdown("### 🚨 High-Risk Customers")
    st.caption("Customers with probability > 50% and at least one churn prediction.")
    df_risk = fetch_high_risk_customers()
    if df_risk.empty:
        st.info("No high-risk customers found yet.")
    else:
        st.dataframe(df_risk, use_container_width=True)


# ── AUDIT LOG ─────────────────────────────────────────────────────────────────

with tab_audit:
    st.markdown("## 🔍 Audit Log")
    st.markdown(
        "Written automatically by two in-memory triggers:\n\n"
        "- `log_new_prediction` — fires on every new prediction\n"
        "- `flag_high_risk` — fires when `probability > 0.75`"
    )

    if st.button("🔄 Refresh", key="refresh_audit"):
        st.rerun()

    df_audit = fetch_audit_log()
    if df_audit.empty:
        st.info("No audit entries yet.")
    else:
        def colour_action(val):
            if val == "HIGH_RISK_FLAGGED":
                return "background-color:#7f1d1d;color:#fca5a5;"
            return "background-color:#1e3a5f;color:#93c5fd;"

        st.dataframe(
            df_audit.style.map(colour_action, subset=["action"]),
            use_container_width=True,
        )
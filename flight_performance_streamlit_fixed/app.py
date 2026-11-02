import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flight Performance Calculator", page_icon="✈️", layout="wide")
st.title("✈️ Aircraft Flight Performance Calculator")
st.caption("Interactive plots based on the aircraft parameters and equations in the provided Colab export. Results are theoretical.")

# Parameters from the provided notebook
rho_table = {0: 1.225, 1: 1.117, 2: 1.006, 3: 0.909, 4: 0.819, 5: 0.736}
st.sidebar.header("Aircraft parameters")
S = st.sidebar.number_input("Wing area S (m²)", 1.0, 300.0, 47.0, 0.5)
AR = st.sidebar.number_input("Aspect ratio AR", 1.0, 20.0, 6.5, 0.1)
e = st.sidebar.number_input("Oswald efficiency e", 0.1, 1.0, 0.87, 0.01)
CD0 = st.sidebar.number_input("Zero-lift drag coefficient CD₀", 0.001, 0.2, 0.032, 0.001, format="%.3f")
W0 = st.sidebar.number_input("Initial aircraft weight W₀ (N)", 1000.0, 500000.0, 103047.0, 1000.0)
CLmax = st.sidebar.number_input("Maximum lift coefficient CLmax", 0.5, 5.0, 2.8, 0.1)
altitude = st.sidebar.selectbox("Altitude (km)", list(rho_table.keys()), index=1)
rho = rho_table[altitude]
K = 1/(np.pi*AR*e)
Vstall = np.sqrt(2*W0/(rho*S*CLmax))
Vmax_plot = st.sidebar.slider("Maximum velocity shown (m/s)", 80, 400, 250, 10)
V = np.linspace(max(5, Vstall), Vmax_plot, 1200)
q = 0.5*rho*V**2
CL = W0/(q*S)
CD = CD0+K*CL**2
D = q*S*CD
Pr = D*V

st.sidebar.markdown("---")
plot_choice = st.sidebar.selectbox("Choose graph", [
    "Power Required vs Velocity", "Thrust Required vs Velocity",
    "Rate of Climb vs Velocity", "Range vs Velocity (Jet)",
    "Range vs Velocity (Piston)", "Endurance vs Velocity (Jet)",
    "Endurance vs Velocity (Piston)", "Glide Angle vs Velocity",
    "Takeoff Trajectory", "V-n Diagram"
])

fig, ax = plt.subplots(figsize=(10,6))
summary = ""

if plot_choice == "Power Required vs Velocity":
    ax.plot(V, Pr/1000, label="Power Required")
    Pavail = st.sidebar.number_input("Power available (kW)", 100.0, 20000.0, 3000.0, 100.0)
    ax.axhline(Pavail, linestyle="--", label="Power Available")
    idx=np.argmin(Pr)
    summary=f"Minimum power required: {Pr[idx]/1000:.2f} kW at {V[idx]:.1f} m/s"
    ax.set_ylabel("Power (kW)")
elif plot_choice == "Thrust Required vs Velocity":
    ax.plot(V, D/1000, label="Thrust Required")
    Tavail=st.sidebar.number_input("Thrust available (N)", 1000.0, 200000.0, 30000.0, 1000.0)
    ax.axhline(Tavail/1000, linestyle="--", label="Thrust Available")
    idx=np.argmin(np.abs(D-Tavail))
    summary=f"Closest thrust intersection: {V[idx]:.1f} m/s"
    ax.set_ylabel("Thrust (kN)")
elif plot_choice == "Rate of Climb vs Velocity":
    Pavail=st.sidebar.number_input("Power available (kW)", 100.0, 20000.0, 3000.0, 100.0)
    ROC=(Pavail*1000-Pr)/W0
    ax.plot(V, ROC, label="Rate of Climb")
    idx=np.argmax(ROC)
    summary=f"Maximum rate of climb: {ROC[idx]:.2f} m/s at {V[idx]:.1f} m/s"
    ax.set_ylabel("Rate of climb (m/s)")
elif plot_choice in ["Range vs Velocity (Jet)", "Range vs Velocity (Piston)", "Endurance vs Velocity (Jet)", "Endurance vs Velocity (Piston)"]:
    fuel_gal=st.sidebar.number_input("Fuel quantity (US gallons)", 100.0, 10000.0, 1900.0, 100.0)
    fuel_density=st.sidebar.number_input("Fuel density (kg/L)", 0.1, 1.5, 0.81, 0.01)
    Wf=fuel_gal*3.78541*fuel_density*9.81
    W1=W0-Wf
    if W1 <= 0:
        st.error("Fuel weight must be less than initial aircraft weight. Adjust fuel quantity or weight.")
        st.stop()
    jet="Jet" in plot_choice
    endurance="Endurance" in plot_choice
    if jet:
        ct=st.sidebar.number_input("Jet TSFC ct (1/s)", 1e-7, 0.01, 1/3600, format="%.7f")
        if endurance:
            y=(1/ct)*(CL/CD)*np.log(W0/W1)/3600
            ylabel="Endurance (hours)"
        else:
            y=(2/ct)*np.sqrt(2/(rho*S))*(np.sqrt(CL)/CD)*(np.sqrt(W0)-np.sqrt(W1))/1000
            ylabel="Range (km)"
    else:
        eta=st.sidebar.number_input("Propeller efficiency ηp", 0.1, 1.0, 0.85, 0.01)
        cp=st.sidebar.number_input("Piston SFC cp (N/(W·s))", 1e-9, 1e-4, 7.46e-7, format="%.2e")
        if endurance:
            y=(eta/cp)*np.sqrt(2*rho*S)*(CL**1.5/CD)*(1/np.sqrt(W1)-1/np.sqrt(W0))/3600
            ylabel="Endurance (hours)"
        else:
            y=(eta/cp)*(CL/CD)*np.log(W0/W1)/1000
            ylabel="Range (km)"
    ax.plot(V,y,label="Performance")
    idx=np.nanargmax(y)
    summary=f"Maximum {ylabel.lower()}: {y[idx]:.2f} at {V[idx]:.1f} m/s"
    ax.set_ylabel(ylabel)
elif plot_choice == "Glide Angle vs Velocity":
    LD=CL/CD
    theta=np.degrees(np.arctan(1/LD))
    ax.plot(V,theta,label="Glide angle")
    idx=np.argmin(theta)
    summary=f"Minimum glide angle: {theta[idx]:.2f}° at {V[idx]:.1f} m/s"
    ax.set_ylabel("Glide angle (degrees)")
elif plot_choice == "Takeoff Trajectory":
    # Simple point-mass trajectory visualization; explicit assumptions shown to the user.
    thrust=st.sidebar.number_input("Takeoff thrust (N)", 1000.0, 200000.0, 30000.0, 1000.0)
    mu=st.sidebar.number_input("Ground rolling friction coefficient μ", 0.0, 0.5, 0.03, 0.01)
    CLto=st.sidebar.number_input("Takeoff lift coefficient", 0.1, 3.0, 1.5, 0.1)
    CDto=CD0+K*CLto**2
    m=W0/9.81
    dt=0.05
    x=z=vel=0.0
    xs=[0.0]; zs=[0.0]
    airborne=False
    for _ in range(10000):
        qloc=0.5*rho*max(vel,0)**2
        lift=qloc*S*CLto
        drag=qloc*S*CDto
        if not airborne and lift >= W0:
            airborne=True
        if airborne:
            vertical_acc=(lift-W0)/m
            horizontal_acc=(thrust-drag)/m
        else:
            horizontal_acc=(thrust-drag-mu*max(W0-lift,0))/m
            vertical_acc=0
        vel=max(0,vel+horizontal_acc*dt)
        x+=vel*dt
        if airborne:
            z=max(0,z+vertical_acc*dt)
        xs.append(x); zs.append(z)
        if airborne and z>=15:
            break
        if x>10000: break
    ax.plot(xs,zs,label="Approximate takeoff path")
    summary=f"Simulated distance to 15 m height: {x:.0f} m; speed at end: {vel:.1f} m/s. Simplified model."
    ax.set_ylabel("Height (m)")
elif plot_choice == "V-n Diagram":
    nmax=st.sidebar.number_input("Positive limit load factor nₘₐₓ", 1.0, 10.0, 3.8, 0.1)
    nmin=st.sidebar.number_input("Negative limit load factor nₘᵢₙ", -5.0, 0.0, -1.52, 0.1)
    Vs=np.sqrt(2*W0/(rho*S*CLmax))
    Va=Vs*np.sqrt(nmax)
    Vd=Vmax_plot
    Vc=0.8*Vd
    Vcurve=np.linspace(0,Vd,500)
    npos=0.5*rho*Vcurve**2*S*CLmax/W0
    nneg=0.5*rho*Vcurve**2*S*(-CLmax)/W0
    ax.plot(Vcurve,np.minimum(npos,nmax),label="Positive stall/limit")
    ax.plot(Vcurve,np.maximum(nneg,nmin),label="Negative stall/limit")
    ax.plot([Va,Vd],[nmax,nmax],"--",label="Positive limit")
    ax.plot([Va,Vd],[nmin,nmin],"--",label="Negative limit")
    ax.axvline(Vc,linestyle=":",label="Design cruise (approx.)")
    ax.set_ylabel("Load factor n")
    summary=f"Stall speed: {Vs:.1f} m/s; maneuvering speed (approx.): {Va:.1f} m/s"

ax.set_xlabel("Velocity (m/s)")
ax.set_title(plot_choice)
ax.grid(True,alpha=0.3)
ax.legend()
fig.tight_layout()
st.pyplot(fig, use_container_width=True)
st.info(summary)
st.caption(f"Altitude selected: {altitude} km | Air density from notebook table: {rho:.3f} kg/m³ | Stall speed: {Vstall:.1f} m/s")
import io
buf=io.BytesIO()
fig.savefig(buf,format="png",dpi=200,bbox_inches="tight")
st.download_button("Download graph as PNG", data=buf.getvalue(), file_name="flight_performance_graph.png", mime="image/png")

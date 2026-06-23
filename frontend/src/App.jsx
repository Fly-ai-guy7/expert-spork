import React, { useEffect, useState } from "react";

const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
const WA = "https://wa.me/201001842081";

async function api(path, options) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

const roomPrice = (r) =>
  r.reference_price == null ? "Price on request" : `from £${r.reference_price}`;

/* Curated experiences (map onto the brand photo placeholders) */
const EXPERIENCES = [
  { label: "Valley of the Kings", cls: "ph-valley", big: true },
  { label: "Temple of Hatshepsut", cls: "ph-hatshepsut", big: true },
  { label: "Hot Air Balloon Rides", cls: "ph-balloon" },
  { label: "Nile Boat Experiences", cls: "ph-boat" },
  { label: "Local Village Walks", cls: "ph-village" },
];

const REVIEWS = [
  { who: "Sarah & Dave", text: "Incredible hospitality and unbeatable Nile views. Ahmed arranged every tour for us." },
  { who: "Jelena L.", text: "Spotless suite, amazing breakfast, and steps from the Valley of the Kings. We'll return!" },
  { who: "Jako L.", text: "An authentic West Bank stay with warm, personalised service from start to finish." },
];

const MAP_PINS = [
  { label: "Valley of the Kings", x: "6%", y: "22%" },
  { label: "Hatshepsut", x: "26%", y: "16%" },
  { label: "Karnak", x: "70%", y: "14%" },
  { label: "Baresk", x: "44%", y: "44%" },
  { label: "West Bank Highlights", x: "12%", y: "70%" },
  { label: "West Bank Boat House", x: "56%", y: "70%" },
];

/* ------------------------------------------------------------------ */
function Header({ view, setView }) {
  return (
    <header className="header">
      <div className="container">
        <a className="brand" href="#top">
          <span className="brand-mark" />
          <span>
            <span className="brand-name">Luxor</span>
            <br />
            <span className="brand-sub">GUEST HOUSE</span>
          </span>
        </a>
        <nav className="nav">
          <a className="nav-extra" href="#experiences">Experiences</a>
          <a className="nav-extra" href="#rooms">Rooms</a>
          <a className="nav-extra" href="#concierge">Concierge</a>
          <div className="viewtoggle">
            <button className={view === "home" ? "active" : ""} onClick={() => setView("home")}>Home</button>
            <button className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}>Dashboard</button>
          </div>
          <a className="btn btn-ghost" href={WA} target="_blank" rel="noreferrer">Contact</a>
        </nav>
      </div>
    </header>
  );
}

function Hero({ contacts }) {
  const r = contacts?.ratings;
  return (
    <section className="hero" id="top">
      <div className="container">
        <h1>Experience the<br />Real Luxor</h1>
        <p>
          Stay on Luxor's historic West Bank and discover ancient Egypt through authentic local
          experiences, breathtaking Nile views, and personalised hospitality.
        </p>
        <div className="hero-cta">
          <a className="btn btn-light" href="#booking">Book Your Stay</a>
          <a className="btn btn-ghost" href="#experiences">Explore Experiences</a>
        </div>
      </div>
      <div className="hero-badges">
        <div className="badge-circle">
          <span className="b1">Luxor</span>
          <span className="b2">DIRECT BOOKING</span>
        </div>
      </div>
      <div className="trust">
        <div className="pill"><span className="ta">Tripadvisor<br />● ● ● ● ●</span></div>
        <div className="pill">
          <span className="score">{r ? r.score.toFixed(1) : "9.0"}</span>
          <span className="bk">Booking.com<br />{r ? `${r.reviews} reviews` : ""}</span>
        </div>
      </div>
    </section>
  );
}

function WhyStay({ trust }) {
  const features = [
    { icon: "📍", label: "Authentic West Bank Location" },
    { icon: "🤝", label: "Local Egyptian Hospitality" },
    { icon: "🏊", label: "Swimming Pool & Terrace" },
    { icon: "🏛️", label: "Easy Access to Valley of the Kings" },
    { icon: "🧭", label: "Personalised Tour Assistance" },
  ];
  return (
    <section className="section cream">
      <div className="container">
        <div className="h-center"><h2>Why Stay With Us</h2></div>
        <div className="feature-row">
          {features.map((f) => (
            <div className="feature" key={f.label}>
              <div className="ic">{f.icon}</div>
              <p>{f.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Experiences() {
  const big = EXPERIENCES.filter((e) => e.big);
  const small = EXPERIENCES.filter((e) => !e.big);
  return (
    <div className="block" id="experiences">
      <h2>Signature Experiences</h2>
      <div className="exp-grid-2">
        {big.map((e) => (
          <a className={`photo ${e.cls}`} key={e.label} href={WA} target="_blank" rel="noreferrer"><span>{e.label}</span></a>
        ))}
      </div>
      <div className="exp-grid-3">
        {small.map((e) => (
          <a className={`photo ${e.cls}`} key={e.label} href={WA} target="_blank" rel="noreferrer"><span>{e.label}</span></a>
        ))}
      </div>
    </div>
  );
}

function FeaturedRoom({ room }) {
  if (!room) return null;
  return (
    <div className="block" id="rooms">
      <h2>Rooms &amp; Suites</h2>
      <article className="room-card">
        <div className="photo ph-suite" />
        <div className="room-info">
          <div className="room-head">
            <h3>{room.name}</h3>
            <span className="stars">★★★★★</span>
          </div>
          <p className="muted" style={{ fontSize: 13 }}>
            {room.size_m2} m² · {room.beds}. Breakfast included.
          </p>
          <ul className="feat">
            {room.amenities.slice(0, 3).map((a) => <li key={a}>{a}</li>)}
          </ul>
          <div className="price"><b>{roomPrice(room)}</b><span>/ night + tax</span></div>
          <div className="room-actions">
            <a className="btn btn-gold" href="#booking">See Availability</a>
            <span style={{ color: "var(--gold-d)", fontWeight: 600, fontSize: 12 }}>Availability now</span>
          </div>
        </div>
      </article>
    </div>
  );
}

function Calendar() {
  const days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"];
  return (
    <div className="cal">
      <h4>Availability 2026</h4>
      <div className="cal-grid">
        {days.map((d) => <div className="d" key={d}>{d}</div>)}
        {Array.from({ length: 30 }, (_, i) => i + 1).map((n) => (
          <div className={`n ${n % 9 === 0 ? "open" : ""}`} key={n}>{n}</div>
        ))}
      </div>
    </div>
  );
}

function MiniRoom({ room }) {
  return (
    <div className="block">
      <h2>Rooms &amp; Suites</h2>
      <div className="card mini">
        <div>
          <div className="photo ph-boat" style={{ marginBottom: 8 }} />
          <h3>{room ? room.name : "Luxury Nile View Suite"}</h3>
          <p className="muted">Nile-view suite with a private balcony and breakfast included.</p>
          <a className="read-more" href="#booking">Read More →</a>
        </div>
        <Calendar />
      </div>
    </div>
  );
}

function Reviews() {
  return (
    <div className="block">
      <h2>Guest Reviews</h2>
      <div className="reviews">
        {REVIEWS.map((r) => (
          <div className="card review" key={r.who}>
            <div className="who">
              <span className="av" />
              <span><b>{r.who}</b><span className="stars">★★★★★</span></span>
            </div>
            <p>{r.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ExploreMap() {
  return (
    <div className="block">
      <h2>Explore Luxor</h2>
      <div className="map ph-map">
        {MAP_PINS.map((p) => (
          <div className="pin" key={p.label} style={{ left: p.x, top: p.y }}>{p.label}</div>
        ))}
      </div>
    </div>
  );
}

function DirectBooking({ rooms }) {
  const empty = { name: "", email: "", check_in: "", check_out: "", guests: 2, room_id: "" };
  const [form, setForm] = useState(empty);
  const [status, setStatus] = useState(null);
  const up = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  async function submit(e) {
    e.preventDefault();
    setStatus({ t: "loading" });
    try {
      const res = await api("/api/bookings", {
        method: "POST",
        body: JSON.stringify({ ...form, guests: Number(form.guests) || null }),
      });
      setStatus({ t: "ok", id: res.booking.id });
      setForm(empty);
    } catch (err) {
      setStatus({ t: "err", m: err.message });
    }
  }

  return (
    <div className="block" id="booking">
      <h2>Direct Booking</h2>
      <form className="card booking" onSubmit={submit}>
        <div className="three">
          <div className="field">
            <label>Arrival Date</label>
            <input type="date" value={form.check_in} onChange={(e) => up("check_in", e.target.value)} />
          </div>
          <div className="field">
            <label>Departure Date</label>
            <input type="date" value={form.check_out} onChange={(e) => up("check_out", e.target.value)} />
          </div>
          <div className="field">
            <label>Guests</label>
            <input type="number" min="1" max="20" value={form.guests} onChange={(e) => up("guests", e.target.value)} />
          </div>
        </div>
        <div className="field">
          <label>Full name</label>
          <input required value={form.name} onChange={(e) => up("name", e.target.value)} placeholder="Jane Traveller" />
        </div>
        <div className="field">
          <label>Email</label>
          <input type="email" required value={form.email} onChange={(e) => up("email", e.target.value)} placeholder="jane@email.com" />
        </div>
        <div className="field">
          <label>Room Selection</label>
          <select value={form.room_id} onChange={(e) => up("room_id", e.target.value)}>
            <option value="">No preference</option>
            {rooms.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
        </div>
        <div style={{ marginTop: 14 }}>
          <button className="btn btn-gold btn-block" type="submit" disabled={status?.t === "loading"}>
            {status?.t === "loading" ? "Sending…" : "Secure Booking"}
          </button>
        </div>
        <p style={{ fontSize: 11, color: "var(--muted)", marginTop: 8, marginBottom: 0 }}>
          No prepayment, no credit card needed. Ahmed confirms availability &amp; final pricing.
        </p>
        {status?.t === "ok" && <p className="alert ok">Thank you! Enquiry received (ref {status.id}).</p>}
        {status?.t === "err" && <p className="alert err">Couldn't send ({status.m}). Try WhatsApp instead.</p>}
      </form>
    </div>
  );
}

function Concierge() {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const suggestions = ["Which rooms have a river view?", "What West Bank tours can I do?", "Is breakfast included?", "How do I book?"];

  async function send(e) {
    e.preventDefault();
    const text = message.trim();
    if (!text) return;
    setHistory((h) => [...h, { role: "you", text }]);
    setMessage("");
    setLoading(true);
    try {
      const res = await api("/api/concierge", { method: "POST", body: JSON.stringify({ message: text }) });
      setHistory((h) => [...h, { role: "bot", text: res.reply, sources: res.sources }]);
    } catch (err) {
      setHistory((h) => [...h, { role: "bot", text: `Sorry, something went wrong (${err.message}).` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="section cream concierge" id="concierge">
      <div className="container">
        <div className="h-center"><h2>Ask the Concierge</h2></div>
        <div className="chips">
          {suggestions.map((s) => <button type="button" className="chip" key={s} onClick={() => setMessage(s)}>{s}</button>)}
        </div>
        <div className="chat">
          {history.map((m, i) => (
            <div className={`bubble ${m.role}`} key={i}>
              <p style={{ margin: 0 }}>{m.text}</p>
              {m.sources?.length > 0 && <p className="src">Sources: {m.sources.join(", ")}</p>}
            </div>
          ))}
          {loading && <div className="bubble bot"><p style={{ margin: 0 }}>Typing…</p></div>}
        </div>
        <form className="chat-form" onSubmit={send}>
          <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask about rooms, tours, breakfast…" aria-label="Message the concierge" />
          <button className="btn btn-gold" type="submit" disabled={loading}>Send</button>
        </form>
      </div>
    </section>
  );
}

function Footer({ contacts }) {
  return (
    <footer className="footer">
      <div className="container">
        <div>
          <div className="brand">
            <span className="brand-mark" />
            <span><span className="brand-name">Luxor</span><br /><span className="brand-sub">GUEST HOUSE</span></span>
          </div>
          <div className="socials">
            <a href="#top">f</a><a href="#top">in</a><a href="#top">ig</a><a href="#top">X</a>
          </div>
        </div>
        <a className="btn btn-wa" href={WA} target="_blank" rel="noreferrer">WhatsApp Us</a>
        <div className="foot-map ph-map" />
        <div className="subscribe">
          <label>Email Subscription</label>
          <div className="row">
            <input type="email" placeholder="you@email.com" />
            <button className="btn btn-gold" type="button">Subscribe</button>
          </div>
          <p style={{ fontSize: 12, marginTop: 10, marginBottom: 0 }}>
            {contacts?.address || "West Bank, Albairat, Alramla, 85111 Luxor, Egypt"}
          </p>
        </div>
      </div>
    </footer>
  );
}

/* ------------------------------------------------------------------ */
function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => { api("/api/dashboard").then(setData).catch((e) => setError(e.message)); }, []);

  if (error) return <div className="container dash"><p className="alert err">Failed to load dashboard: {error}</p></div>;
  if (!data) return <div className="container dash"><p>Loading dashboard…</p></div>;
  const k = data.kpis;
  const tiles = [
    ["Rooms", k.total_rooms], ["Tours", k.total_tours], ["Bookable tours", k.bookable_tours],
    ["On request", k.tours_on_request], ["Total enquiries", k.total_enquiries], ["New enquiries", k.new_enquiries],
    ["Avg room £", k.avg_room_reference_price_gbp], ["Rating", `${k.rating} (${k.reviews})`],
  ];
  return (
    <div className="container dash">
      <h1>Operations Dashboard</h1>
      <div className="kpis">
        {tiles.map(([l, v]) => <div className="kpi" key={l}><b>{v}</b><span>{l}</span></div>)}
      </div>
      <h2 style={{ marginBottom: 8 }}>Enquiries</h2>
      {data.recent_enquiries.length === 0 ? <p className="muted">No enquiries yet.</p> : (
        <table className="table">
          <thead><tr><th>Created</th><th>Name</th><th>Email</th><th>Room</th><th>Guests</th><th>Status</th></tr></thead>
          <tbody>
            {data.recent_enquiries.map((b) => (
              <tr key={b.id}>
                <td>{(b.created_at || "").slice(0, 16).replace("T", " ")}</td>
                <td>{b.name}</td><td>{b.email}</td><td>{b.room_id || "—"}</td><td>{b.guests || "—"}</td><td>{b.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <h2 style={{ marginBottom: 8 }}>Rooms</h2>
      <table className="table">
        <thead><tr><th>Name</th><th>Size</th><th>Sleeps</th><th>Ref price</th></tr></thead>
        <tbody>{data.rooms.map((r) => <tr key={r.id}><td>{r.name}</td><td>{r.size_m2} m²</td><td>{r.capacity_adults}</td><td>{roomPrice(r)}</td></tr>)}</tbody>
      </table>
    </div>
  );
}

/* ------------------------------------------------------------------ */
export default function App() {
  const [view, setView] = useState("home");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api("/api/rooms"), api("/api/contacts")])
      .then(([rooms, contacts]) => setData({ rooms, contacts }))
      .catch((e) => setError(e.message));
  }, []);

  const rooms = data?.rooms || [];
  const contacts = data?.contacts;

  return (
    <div className="app">
      <Header view={view} setView={setView} />
      {view === "dashboard" ? (
        <main style={{ paddingTop: 80 }}><Dashboard /></main>
      ) : (
        <main>
          <Hero contacts={contacts} />
          <WhyStay trust={contacts?.trust_signals} />
          <section className="section body">
            <div className="container body-grid">
              <div className="col">
                <Experiences />
                <FeaturedRoom room={rooms[0]} />
              </div>
              <div className="col">
                <MiniRoom room={rooms[1]} />
                <Reviews />
                <ExploreMap />
                <DirectBooking rooms={rooms} />
              </div>
            </div>
          </section>
          <Concierge />
        </main>
      )}
      <Footer contacts={contacts} />
    </div>
  );
}

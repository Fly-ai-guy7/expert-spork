import React, { useEffect, useState } from "react";

const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
const WHATSAPP_LINK = "https://wa.me/201001842081";

async function api(path, options) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${detail}`);
  }
  return res.json();
}

function priceForRoom(room) {
  if (room.reference_price == null) return "Price on request";
  return `from £${room.reference_price} ${room.price_note || ""}`.trim();
}

function priceForTour(tour) {
  if (tour.price_on_request || tour.price == null) return "Price on request";
  return `$${tour.price}`;
}

/* --------------------------------------------------------------------- */
/* Shared bits                                                            */
/* --------------------------------------------------------------------- */
function WhatsAppButton({ label = "Chat on WhatsApp", text }) {
  const href = text ? `${WHATSAPP_LINK}?text=${encodeURIComponent(text)}` : WHATSAPP_LINK;
  return (
    <a className="btn btn-whatsapp" href={href} target="_blank" rel="noreferrer">
      {label}
    </a>
  );
}

/* --------------------------------------------------------------------- */
/* Home view                                                             */
/* --------------------------------------------------------------------- */
function Hero({ contacts }) {
  const r = contacts?.ratings;
  return (
    <header className="hero">
      <div className="hero-inner">
        <p className="eyebrow">West Bank · Luxor · Egypt</p>
        <h1>Luxor Guest House</h1>
        <p className="lede">
          Nile-side apartments moments from the Valley of the Kings. Breakfast included,
          no prepayment, and no credit card needed to reserve.
        </p>
        <div className="trust-row">
          {(contacts?.trust_signals || []).map((t) => (
            <span className="trust-pill" key={t}>✓ {t}</span>
          ))}
        </div>
        {r && (
          <p className="rating-line">
            <strong>{r.score?.toFixed(1)}</strong> / 10 on {r.source} · {r.reviews} reviews
          </p>
        )}
        <div className="hero-cta">
          <a className="btn btn-primary" href="#enquire">Make an enquiry</a>
          <WhatsAppButton />
        </div>
        <p className="addr">{contacts?.address}</p>
      </div>
    </header>
  );
}

function Rooms({ rooms }) {
  return (
    <section id="rooms" className="section">
      <h2>Rooms &amp; Apartments</h2>
      <div className="card-grid">
        {rooms.map((room) => (
          <article className="card" key={room.id}>
            <div className="card-head">
              <h3>{room.name}</h3>
              <span className="price">{priceForRoom(room)}</span>
            </div>
            <p className="muted">
              {room.size_m2} m² · sleeps {room.capacity_adults} · {room.beds}
            </p>
            <ul className="amenities">
              {room.amenities.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
            <WhatsAppButton
              label="Enquire about this room"
              text={`Hello Ahmed, I'd like to ask about the ${room.name} at Luxor Guest House.`}
            />
          </article>
        ))}
      </div>
    </section>
  );
}

function Tours({ tours }) {
  return (
    <section id="tours" className="section">
      <h2>Tours &amp; Experiences</h2>
      <div className="tour-grid">
        {tours.map((tour) => (
          <div className="tour" key={tour.id}>
            <div>
              <span className="tour-area">{tour.area}</span>
              <p className="tour-name">{tour.name}</p>
              {tour.notes && <p className="muted small">{tour.notes}</p>}
            </div>
            <span className="tour-price">{priceForTour(tour)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Concierge() {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  async function send(e) {
    e.preventDefault();
    const text = message.trim();
    if (!text) return;
    setHistory((h) => [...h, { role: "you", text }]);
    setMessage("");
    setLoading(true);
    try {
      const res = await api("/api/concierge", {
        method: "POST",
        body: JSON.stringify({ message: text }),
      });
      setHistory((h) => [...h, { role: "concierge", text: res.reply, sources: res.sources }]);
    } catch (err) {
      setHistory((h) => [...h, { role: "concierge", text: `Sorry, something went wrong (${err.message}).` }]);
    } finally {
      setLoading(false);
    }
  }

  const suggestions = [
    "Which rooms have a river view?",
    "What tours can I do on the West Bank?",
    "Is breakfast included?",
    "How do I book?",
  ];

  return (
    <section id="concierge" className="section">
      <h2>Ask the Concierge</h2>
      <p className="muted">
        Ask about rooms, tours, breakfast, payment or check-in — answered instantly from our own information.
      </p>
      <div className="suggestions">
        {suggestions.map((s) => (
          <button key={s} type="button" className="chip" onClick={() => setMessage(s)}>
            {s}
          </button>
        ))}
      </div>
      <div className="chat">
        {history.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            <p>{m.text}</p>
            {m.sources?.length > 0 && (
              <p className="sources">Sources: {m.sources.join(", ")}</p>
            )}
          </div>
        ))}
        {loading && <div className="bubble concierge"><p>Typing…</p></div>}
      </div>
      <form className="chat-form" onSubmit={send}>
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your question…"
          aria-label="Message the concierge"
        />
        <button className="btn btn-primary" type="submit" disabled={loading}>Send</button>
      </form>
    </section>
  );
}

function EnquiryForm({ rooms, tours }) {
  const empty = {
    name: "", email: "", phone: "", room_id: "",
    check_in: "", check_out: "", guests: 2, tours: [], message: "",
  };
  const [form, setForm] = useState(empty);
  const [status, setStatus] = useState(null);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  function toggleTour(id) {
    setForm((f) => ({
      ...f,
      tours: f.tours.includes(id) ? f.tours.filter((t) => t !== id) : [...f.tours, id],
    }));
  }

  async function submit(e) {
    e.preventDefault();
    setStatus({ type: "loading" });
    try {
      const payload = { ...form, guests: Number(form.guests) || null };
      const res = await api("/api/bookings", { method: "POST", body: JSON.stringify(payload) });
      setStatus({ type: "success", id: res.booking.id });
      setForm(empty);
    } catch (err) {
      setStatus({ type: "error", message: err.message });
    }
  }

  return (
    <section id="enquire" className="section">
      <h2>Booking Enquiry</h2>
      <p className="muted">
        No prepayment, no credit card — send your details and Ahmed will confirm availability and final pricing.
      </p>
      <form className="form" onSubmit={submit}>
        <div className="form-row">
          <label>
            Full name *
            <input required value={form.name} onChange={(e) => update("name", e.target.value)} />
          </label>
          <label>
            Email *
            <input type="email" required value={form.email} onChange={(e) => update("email", e.target.value)} />
          </label>
        </div>
        <div className="form-row">
          <label>
            Phone / WhatsApp
            <input value={form.phone} onChange={(e) => update("phone", e.target.value)} />
          </label>
          <label>
            Guests
            <input type="number" min="1" max="20" value={form.guests} onChange={(e) => update("guests", e.target.value)} />
          </label>
        </div>
        <div className="form-row">
          <label>
            Check-in
            <input type="date" value={form.check_in} onChange={(e) => update("check_in", e.target.value)} />
          </label>
          <label>
            Check-out
            <input type="date" value={form.check_out} onChange={(e) => update("check_out", e.target.value)} />
          </label>
        </div>
        <label>
          Room
          <select value={form.room_id} onChange={(e) => update("room_id", e.target.value)}>
            <option value="">No preference</option>
            {rooms.map((r) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
        </label>
        <fieldset className="tours-pick">
          <legend>Tours you're interested in (optional)</legend>
          <div className="tours-pick-grid">
            {tours.map((t) => (
              <label key={t.id} className="checkbox">
                <input
                  type="checkbox"
                  checked={form.tours.includes(t.id)}
                  onChange={() => toggleTour(t.id)}
                />
                {t.name}
              </label>
            ))}
          </div>
        </fieldset>
        <label>
          Message
          <textarea
            rows="3"
            value={form.message}
            onChange={(e) => update("message", e.target.value)}
            placeholder="Anything else we should know?"
          />
        </label>
        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={status?.type === "loading"}>
            {status?.type === "loading" ? "Sending…" : "Send enquiry"}
          </button>
          <WhatsAppButton label="Or message us directly" />
        </div>
        {status?.type === "success" && (
          <p className="alert success">Thank you! Your enquiry was received (ref {status.id}). We'll be in touch shortly.</p>
        )}
        {status?.type === "error" && (
          <p className="alert error">Sorry, we couldn't send that ({status.message}). Please try WhatsApp.</p>
        )}
      </form>
    </section>
  );
}

function HomeView({ data }) {
  return (
    <>
      <Hero contacts={data.contacts} />
      <main className="container">
        <Rooms rooms={data.rooms} />
        <Tours tours={data.tours} />
        <Concierge />
        <EnquiryForm rooms={data.rooms} tours={data.tours} />
      </main>
    </>
  );
}

/* --------------------------------------------------------------------- */
/* Dashboard view                                                        */
/* --------------------------------------------------------------------- */
function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api("/api/dashboard").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <main className="container"><p className="alert error">Failed to load dashboard: {error}</p></main>;
  if (!data) return <main className="container"><p>Loading dashboard…</p></main>;

  const k = data.kpis;
  const kpiList = [
    { label: "Rooms", value: k.total_rooms },
    { label: "Tours", value: k.total_tours },
    { label: "Bookable tours", value: k.bookable_tours },
    { label: "On request", value: k.tours_on_request },
    { label: "Total enquiries", value: k.total_enquiries },
    { label: "New enquiries", value: k.new_enquiries },
    { label: "Avg room (£)", value: k.avg_room_reference_price_gbp },
    { label: "Rating", value: `${k.rating} (${k.reviews})` },
  ];

  return (
    <main className="container dashboard">
      <h1>Operations Dashboard</h1>
      <div className="kpi-grid">
        {kpiList.map((kpi) => (
          <div className="kpi" key={kpi.label}>
            <span className="kpi-value">{kpi.value}</span>
            <span className="kpi-label">{kpi.label}</span>
          </div>
        ))}
      </div>

      <h2>Enquiries</h2>
      {data.recent_enquiries.length === 0 ? (
        <p className="muted">No enquiries yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr><th>Created</th><th>Name</th><th>Email</th><th>Room</th><th>Guests</th><th>Status</th></tr>
          </thead>
          <tbody>
            {data.recent_enquiries.map((b) => (
              <tr key={b.id}>
                <td>{(b.created_at || "").slice(0, 16).replace("T", " ")}</td>
                <td>{b.name}</td>
                <td>{b.email}</td>
                <td>{b.room_id || "—"}</td>
                <td>{b.guests || "—"}</td>
                <td>{b.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2>Rooms</h2>
      <table className="table">
        <thead><tr><th>Name</th><th>Size</th><th>Sleeps</th><th>Ref price</th></tr></thead>
        <tbody>
          {data.rooms.map((r) => (
            <tr key={r.id}>
              <td>{r.name}</td><td>{r.size_m2} m²</td><td>{r.capacity_adults}</td><td>{priceForRoom(r)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Tours</h2>
      <table className="table">
        <thead><tr><th>Name</th><th>Area</th><th>Price</th></tr></thead>
        <tbody>
          {data.tours.map((t) => (
            <tr key={t.id}>
              <td>{t.name}</td><td>{t.area}</td><td>{priceForTour(t)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

/* --------------------------------------------------------------------- */
/* Root                                                                  */
/* --------------------------------------------------------------------- */
export default function App() {
  const [view, setView] = useState("home");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api("/api/rooms"),
      api("/api/tours"),
      api("/api/contacts"),
    ])
      .then(([rooms, tours, contacts]) => setData({ rooms, tours, contacts }))
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="app">
      <nav className="nav">
        <span className="brand">Luxor Guest House</span>
        <div className="nav-links">
          <button className={view === "home" ? "active" : ""} onClick={() => setView("home")}>Home</button>
          <button className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}>Dashboard</button>
        </div>
      </nav>

      {view === "dashboard" ? (
        <Dashboard />
      ) : error ? (
        <main className="container">
          <p className="alert error">Couldn't reach the API at {API_URL} ({error}).</p>
        </main>
      ) : !data ? (
        <main className="container"><p>Loading…</p></main>
      ) : (
        <HomeView data={data} />
      )}

      <footer className="footer">
        <p>Luxor Guest House · West Bank, Albairat, Alramla, 85111 Luxor, Egypt</p>
        <p>
          WhatsApp <a href={WHATSAPP_LINK} target="_blank" rel="noreferrer">+20 100 184 2081</a>
          {" · "}info@luxorguesthouse.local
        </p>
      </footer>
    </div>
  );
}

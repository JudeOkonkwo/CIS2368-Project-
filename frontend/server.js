const express = require("express");
const axios = require("axios");
const path = require("path");

const app = express();
const PORT = 3000;
const API_BASE_URL = "http://127.0.0.1:5000";

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

async function getApiData(endpoint) {
  const response = await axios.get(`${API_BASE_URL}${endpoint}`);
  return response.data;
}

function getErrorMessage(error) {
  if (error.response && error.response.data && error.response.data.error) {
    return error.response.data.error;
  }

  if (error.message) {
    return error.message;
  }

  return "Something went wrong.";
}

app.get("/", async (req, res) => {
  try {
    const members = await getApiData("/api/member/all");
    const events = await getApiData("/api/event/all");
    const registrations = await getApiData("/api/registration/all");

    let selectedEventMembers = [];
    let selectedEventName = "";

    if (req.query.eventId) {
      selectedEventMembers = await getApiData(`/api/eventmembers?id=${req.query.eventId}`);

      const selectedEvent = events.find((event) => String(event.id) === String(req.query.eventId));
      selectedEventName = selectedEvent ? `${selectedEvent.name} - ${selectedEvent.date}` : "";
    }

    res.render("index", {
      members,
      events,
      registrations,
      selectedEventMembers,
      selectedEventName,
      message: req.query.message || "",
      error: req.query.error || ""
    });
  } catch (error) {
    res.render("index", {
      members: [],
      events: [],
      registrations: [],
      selectedEventMembers: [],
      selectedEventName: "",
      message: "",
      error: "Could not connect to the Flask API. Make sure backend/app.py is running on port 5000."
    });
  }
});

app.post("/members/add", async (req, res) => {
  try {
    await axios.post(`${API_BASE_URL}/api/member`, {
      name: req.body.name,
      details: req.body.details,
      title: req.body.title,
      level: req.body.level
    });

    res.redirect("/?message=Member added successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/members/update", async (req, res) => {
  try {
    await axios.put(`${API_BASE_URL}/api/member`, {
      id: Number(req.body.id),
      name: req.body.name,
      details: req.body.details,
      title: req.body.title,
      level: req.body.level
    });

    res.redirect("/?message=Member updated successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/members/delete", async (req, res) => {
  try {
    await axios.delete(`${API_BASE_URL}/api/member`, {
      data: {
        id: Number(req.body.id)
      }
    });

    res.redirect("/?message=Member deleted successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/events/add", async (req, res) => {
  try {
    await axios.post(`${API_BASE_URL}/api/event`, {
      name: req.body.name,
      capacity: Number(req.body.capacity),
      level: req.body.level,
      date: req.body.date
    });

    res.redirect("/?message=Event added successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/events/update", async (req, res) => {
  try {
    await axios.put(`${API_BASE_URL}/api/event`, {
      id: Number(req.body.id),
      name: req.body.name,
      capacity: Number(req.body.capacity),
      level: req.body.level,
      date: req.body.date
    });

    res.redirect("/?message=Event updated successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/events/delete", async (req, res) => {
  try {
    await axios.delete(`${API_BASE_URL}/api/event`, {
      data: {
        id: Number(req.body.id)
      }
    });

    res.redirect("/?message=Event deleted successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/registrations/add", async (req, res) => {
  try {
    await axios.post(`${API_BASE_URL}/api/registration`, {
      event_id: Number(req.body.event_id),
      member_id: Number(req.body.member_id)
    });

    res.redirect("/?message=Registration added successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/registrations/update", async (req, res) => {
  try {
    await axios.put(`${API_BASE_URL}/api/registration`, {
      id: Number(req.body.id),
      event_id: Number(req.body.event_id),
      member_id: Number(req.body.member_id)
    });

    res.redirect("/?message=Registration updated successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.post("/registrations/delete", async (req, res) => {
  try {
    await axios.delete(`${API_BASE_URL}/api/registration`, {
      data: {
        id: Number(req.body.id)
      }
    });

    res.redirect("/?message=Registration deleted successfully");
  } catch (error) {
    res.redirect(`/?error=${encodeURIComponent(getErrorMessage(error))}`);
  }
});

app.get("/event-members", (req, res) => {
  const eventId = req.query.eventId;

  if (!eventId) {
    return res.redirect("/?error=Please select an event");
  }

  return res.redirect(`/?eventId=${eventId}`);
});

app.listen(PORT, () => {
  console.log(`Frontend running at http://localhost:${PORT}`);
});

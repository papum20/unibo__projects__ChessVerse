import { Modal } from "react-bootstrap";
import { useState, useEffect } from "react";
import { Trophy } from "react-bootstrap-icons";
import { Button } from "@mui/material";
import BasicTabs from "./BasicTabs.jsx";
import { API } from "../const/const_api.js";
import { joinPaths } from "../utils/path";
import { SERVER_ADDR } from "../const/const";

function Scores() {
  const [showModal, setShowModal] = useState(false);

  const [focus, setFocus] = useState("daily board");

  // Array di oggetti che tiene traccia di username e dato elo o altre cose in base in che sezione sei
  const [data, setData] = useState([]);

  

  async function fetchLeaderboard(API, date=null) {
    const url = date ? `${API}?date=${date}` : API;
    const response = await fetch(joinPaths(SERVER_ADDR, url));
    return await response.json();
  }

  const getWeeklyDateString = () => {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 1);
    const weekNo = Math.ceil(
      ((now - start) / 86400000 + start.getDay() + 1) / 7
    );
    return `${weekNo < 10 ? "0" + weekNo : weekNo}${now.getFullYear()}`;
  };

  const getCurrentLeaderboard = async () => {
    if (focus === "daily board") {
      setData((await fetchLeaderboard(API.dailyLeaderboard.endpoint, new Date().toLocaleDateString("en-GB").split('/').join(''))).daily_leaderboard);
    } else if (focus === "weekly challenge") {
      setData((await fetchLeaderboard(API.weeklyLeaderboard.endpoint, getWeeklyDateString())).weekly_leaderboard);
    } else if (focus === "ranked") {
      setData((await fetchLeaderboard(API.rankedLeaderboard.endpoint)).ranked_leaderboard)
    } else {
      setData((await fetchLeaderboard(API.multiplayerLeaderboard.endpoint)).multiplayer_leaderboard)
    }
  }

  useEffect(() => {
    getCurrentLeaderboard();
  }, [focus]);


  return (
    <>
      <Modal show={showModal} fullscreen>
        <BasicTabs
          data={data}
          setFocus={setFocus}
          setShowModal={setShowModal}
        />
      </Modal>

      <div
        style={{ display: "flex", justifyContent: "center", marginTop: "30px" }}
      >
        <Button
          color="brown"
          onClick={() => setShowModal(true)}
          style={{ fontSize: "1.5rem", borderRadius: "20px" }}
          variant="contained"
        >
          <div
            style={{
              marginTop: "5px",
              marginBottom: "5px",
            }}
          >
            <Trophy size="30" style={{ marginTop: "-5px" }} />
            <span style={{ marginLeft: "10px" }}>Scores</span>
          </div>
        </Button>
      </div>
    </>
  );
}

export default Scores;

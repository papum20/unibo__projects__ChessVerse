import { Modal } from "react-bootstrap";
import { useState, useEffect } from "react";
import { Trophy } from "react-bootstrap-icons";
import { Button } from "@mui/material";
import BasicTabs from "./BasicTabs.jsx";
import { API } from "../const/const_api.js"


function Scores (){
    const [showModal, setShowModal] = useState(false);

    const [focus, setFocus] = useState("daily board");

    // Array di oggetti che tiene traccia di username e dato elo o altre cose in base in che sezione sei
    const [data, setData] = useState([]);

    async function fetchLeaderboard(API, tag){
        const response = await fetch(API);
        const leaderboards = await response.json();
        return leaderboards[tag][-1];
    }

    async function getCurrentLeaderboard (){
        if (focus === "daily board") {
            const currentLeaderboard = await fetchLeaderboard(
              API.dailyLeaderboard.endpoint, 'daily_leaderboard'
            );
            setData(currentLeaderboard);
        }
        else if (focus === "weekly challenge") {
            const currentLeaderboard = await fetchLeaderboard(
              API.weeklyLeaderboard.endpoint, 'weekly_leaderboard'
            );
            setData(currentLeaderboard);
        }
        else if (focus === "ranked") {
            const currentLeaderboard = await fetchLeaderboard(
              API.rankedLeaderboard.endpoint, ''
            );
            setData(currentLeaderboard);
        }
        else {
            //fai la fetch al server e ottieni i dati
            setData([{username: "pippo", elo: 10}, {username: "pippo", elo: 10}])
        }
    }

    useEffect(()=>{
        getCurrentLeaderboard();
    },[focus])

    return (
            <>
                <Modal show={showModal} fullscreen>  
                    <BasicTabs data={data} setFocus={setFocus} setShowModal={setShowModal}/>
                </Modal>

                <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                    <Button
                        color="brown"
                        onClick={()=>setShowModal(true)}
                        style={{fontSize: "1.5rem", borderRadius: "20px"}}
                        variant="contained"
                    >
                        <div style={{
                            marginTop: "5px",
                            marginBottom: "5px",
                        }}>
                            <Trophy size="30" style={{marginTop: "-5px"}} />
                            <span style={{marginLeft: "10px"}}>Scores</span>
                        </div>
                    </Button>
                </div>
            </>
        )
}

export default Scores;
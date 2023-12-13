
import {Modal} from "react-bootstrap";
import {useState, useEffect} from "react";
import {Trophy} from "react-bootstrap-icons";
import { Button} from "@mui/material";
import BasicTabs from "./BasicTabs.jsx";


function Scores (){



   const [showModal, setShowModal] = useState(false);

    const [focus, setFocus] = useState("daily board");

    //array di oggetti che tiene traccia di username e dato elo o altre cose in base in che sezione sei
    const [data, setData] = useState([]);

    function getCurrentLeaderboard (){
        if(focus==="daily board"){
            //fai la fetch al server e ottieni i dati
            setData([{username: "pippo", minMoves: 10},{username: "pippo", minMoves: 10}])
        }
        else if(focus==="weekly challenge"){
            //fai la fetch al server e ottieni i dati
            setData([{username: "pluto", minMoves: 10},{username: "pippo", minMoves: 10}])
        }
        else if(focus==="ranked"){
            //fai la fetch al server e ottieni i dati
            setData([{username: "pippo", rank: 10},{username: "pippo", rank: 10}])
        }
        else{
            //fai la fetch al server e ottieni i dati
            setData([{username: "pippo", elo: 10},{username: "pippo", elo: 10}])
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
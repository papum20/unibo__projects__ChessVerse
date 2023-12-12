
import {Modal} from "react-bootstrap";
import {useState} from "react";
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
            setData([{username: "pippo", minMoves: 10},])
        }
    }

    return (
            <>
                <Modal show={showModal} fullscreen>  
                    <BasicTabs setFocus={setFocus} setShowModal={setShowModal}/>
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
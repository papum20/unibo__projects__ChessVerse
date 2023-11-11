import {useNavigate } from "react-router-dom";
import { Button } from "@mui/material";


function Signup (){
    const navigator = useNavigate();


    return (
        <div style={{marginTop: "30%", marginLeft: "40%"}}>
            <span>torna alla pagina di </span>
            <Button variant="contained" onClick={()=>{navigator("../", { relative: "path" });}}>
                start
            </Button>
        </div>
    )
}
export default Signup;
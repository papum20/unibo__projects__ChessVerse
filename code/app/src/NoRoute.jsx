import { Button } from "@mui/material";
import { Link } from "react-router-dom";
function NoRoute () {

    return (
        <div style={{marginTop: "30%", marginLeft: "40%"}}>
            <span>torna alla pagina di </span>
            <Button as={Link} to="/" variant="contained" >
                start
            </Button>
        </div>
    )

}
export default NoRoute;
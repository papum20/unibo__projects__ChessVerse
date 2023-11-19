import { useNavigate } from "react-router-dom";
import { Button } from "@mui/material";

function Login () {
    const navigator = useNavigate();

    return (
        <div style={{marginTop: "30%", marginLeft: "40%"}}>
            <span data-testid="loginSpan">torna alla pagina di </span>
            <Button
              variant="contained"
              onClick={()=> {
                navigator("../", { relative: "path" });
              }}

              data-testid="loginButton"
            >
                start
            </Button>
        </div>
    )
}
export default Login;
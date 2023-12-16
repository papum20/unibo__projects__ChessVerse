import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "../styles/Alert.css";

//documentazione a https://www.makeuseof.com/react-toastify-custom-alerts-create/

function Alert() {
  return (
    <div>
      <ToastContainer position="top-left" autoClose={2000} />
    </div>
  );
}

export default Alert;

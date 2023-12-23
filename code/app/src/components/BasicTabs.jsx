import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { CloseButton, Row, Col, Form, Modal } from "react-bootstrap";
import { Tabs, Tab, Box } from "@mui/material";
import "../styles/BasicTabs.css";
import { MOBILEWIDTH } from "../const/const.js";
import useWindowDimensions from "./useWindowDimensions.jsx";
import { Calendar } from "react-bootstrap-icons";

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`vertical-tabpanel-${index}`}
      aria-labelledby={`vertical-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

function a11yProps(index) {
  return {
    id: `vertical-tab-${index}`,
    "aria-controls": `vertical-tabpanel-${index}`,
  };
}

export default function BasicTabs(props) {
  const [value, setValue] = useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const { width, height } = useWindowDimensions();
  const [selectedDate, setSelectedDate] = useState(new Date());

  const [showMDate, setShowMDate] = useState(false);
  const [isDaily, setIsDaily] = useState(false);

  return (
    <Box sx={{ flexGrow: 1, display: "flex", height: "80vh" }}>
      <Tabs
        orientation="vertical"
        value={value}
        onChange={handleChange}
        aria-label="Vertical tabs example"
        sx={{ borderRight: 1, borderColor: "divider" }}
        style={{ backgroundColor: "rgb(101, 67, 33)" }}
      >
        <Tab
          style={{ color: "white", marginTop: "20px" }}
          onClick={() => props.setFocus("daily board")}
          label="Daily Board"
          {...a11yProps(0)}
        />
        <Tab
          style={{ color: "white" }}
          label="Weekly challenge"
          onClick={() => props.setFocus("weekly challenge")}
          {...a11yProps(1)}
        />
        <Tab
          style={{ color: "white" }}
          label="Ranked"
          onClick={() => props.setFocus("ranked")}
          {...a11yProps(2)}
        />
        <Tab
          style={{ color: "white" }}
          label="1v1"
          onClick={() => props.setFocus("1v1")}
          {...a11yProps(3)}
        />
      </Tabs>

      <Modal show={showMDate} centered>
        <div style={{ backgroundColor: "rgb(81, 57, 23)" }}>
          <Modal.Title style={{ display: "flex", justifyContent: "flex-end" }}>
            <CloseButton
              style={{ marginTop: "5px", marginRight: "5px" }}
              onClick={() => setShowMDate(false)}
            />
          </Modal.Title>
          <Modal.Body style={{ marginTop: "20px", marginBottom: "30px" }}>
            <Form.Control
              onChange={(e) => {
                props.setDateArr(
                  e.target.value
                    .split("-")
                    .reverse()
                    .map((obj) => parseInt(obj)) /* [GG,MM,YYYY] */,
                );
              }}
              type="date"
              style={{ fontSize: "25px" }}
            />
          </Modal.Body>
        </div>
      </Modal>

      <div style={{ backgroundColor: "rgb(150, 111, 51)", width: "95vw" }}>
        <>
          <TabPanel value={value} index={0}>
            <Row style={{ marginBottom: "20px" }}>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  Username
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  mosse
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "space-between" }}>
                <Calendar
                  onClick={() => {
                    setShowMDate(true);
                    setIsDaily(true);
                  }}
                  size={25}
                  style={{ cursor: "pointer", marginTop: "5px" }}
                />
                <CloseButton onClick={() => props.setShowModal(false)} />
              </Col>
            </Row>
            <div
              style={{
                overflow: "auto",
                overflowX: "hidden",
                maxHeight: "80vh",
              }}
            >
              {props.data.map((el, i) => (
                <Row style={{ marginBottom: "10px" }} key={i}>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.username}</span>
                  </Col>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.moves_count}</span>
                  </Col>
                  <Col
                    style={{ display: "flex", justifyContent: "flex-end" }}
                  ></Col>
                </Row>
              ))}
            </div>
          </TabPanel>
          <TabPanel value={value} index={1}>
            <Row style={{ marginBottom: "20px" }}>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  Username
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  mosse
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "space-between" }}>
                <Calendar
                  onClick={() => {
                    setShowMDate(true);
                    setIsDaily(false);
                  }}
                  size={25}
                  style={{ cursor: "pointer", marginTop: "5px" }}
                />
                <CloseButton onClick={() => props.setShowModal(false)} />
              </Col>
            </Row>
            <div
              style={{
                overflow: "auto",
                overflowX: "hidden",
                maxHeight: "80vh",
              }}
            >
              {props.data.map((el, i) => (
                <Row style={{ marginBottom: "10px" }} key={i}>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.username}</span>
                  </Col>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.moves_count}</span>
                  </Col>
                  <Col
                    style={{ display: "flex", justifyContent: "flex-end" }}
                  ></Col>
                </Row>
              ))}
            </div>
          </TabPanel>
          <TabPanel value={value} index={2}>
            <Row style={{ marginBottom: "20px" }}>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  Username
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  Rank
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "flex-end" }}>
                <CloseButton onClick={() => props.setShowModal(false)} />
              </Col>
            </Row>
            <div
              style={{
                overflow: "auto",
                overflowX: "hidden",
                maxHeight: "80vh",
              }}
            >
              {props.data.map((el, i) => (
                <Row style={{ marginBottom: "10px" }} key={i}>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.username}</span>
                  </Col>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.score_ranked}</span>
                  </Col>
                  <Col
                    style={{ display: "flex", justifyContent: "flex-end" }}
                  ></Col>
                </Row>
              ))}
            </div>
          </TabPanel>
          <TabPanel value={value} index={3}>
            <Row style={{ marginBottom: "20px" }}>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  Username
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "center" }}>
                <span
                  style={{
                    fontWeight: "bold",
                    fontSize: `${width < MOBILEWIDTH ? "16px" : "22px"}`,
                  }}
                >
                  Elo
                </span>
              </Col>
              <Col style={{ display: "flex", justifyContent: "flex-end" }}>
                <CloseButton onClick={() => props.setShowModal(false)} />
              </Col>
            </Row>
            <div
              style={{
                overflow: "auto",
                overflowX: "hidden",
                maxHeight: "80vh",
              }}
            >
              {props.data.map((el, i) => (
                <Row style={{ marginBottom: "10px" }} key={i}>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.username}</span>
                  </Col>
                  <Col style={{ display: "flex", justifyContent: "center" }}>
                    <span>{el.EloReallyBadChess}</span>
                  </Col>
                  <Col
                    style={{ display: "flex", justifyContent: "flex-end" }}
                  ></Col>
                </Row>
              ))}
            </div>
          </TabPanel>
        </>
      </div>
    </Box>
  );
}

import * as React from 'react';
import PropTypes from 'prop-types';
import {CloseButton, Row, Col} from "react-bootstrap";
import {Tabs, Tab, Box} from "@mui/material"

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
      {value === index && (
        <Box sx={{ p: 3 }}>
          <>{children}</>
        </Box>
      )}
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
    'aria-controls': `vertical-tabpanel-${index}`,
  };
}

export default function BasicTabs(props) {
  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Box
      sx={{ flexGrow: 1, display: 'flex', height: "80vh" }}
    >
      <Tabs style={{backgroundColor: "rgb(101, 67, 33)"}}
        orientation="vertical"
       
        value={value}
        onChange={handleChange}
        aria-label="Vertical tabs example"
        sx={{ borderRight: 1, borderColor: 'divider' }}
      >
        <Tab style={{color: "white", marginTop: "20px"}} onClick={()=> props.setFocus("daily board")} label="Daily Board" {...a11yProps(0)} />
        <Tab style={{color: "white"}} label="Weekly challenge" onClick={()=> props.setFocus("weekly challenge")} {...a11yProps(1)} />
        <Tab style={{color: "white"}} label="Ranked" onClick={()=> props.setFocus("ranked")} {...a11yProps(2)} />
        <Tab style={{color: "white"}} label="1v1" onClick={()=> props.setFocus("1v1")} {...a11yProps(3)} />
      </Tabs>
      
      <div style={{backgroundColor: "rgb(150, 111, 51)", width: "95vw"}}>
        <TabPanel value={value} index={0}>
            <Row style={{marginBottom: "20px"}}>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Username</span>
                </Col>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Turni Minimi</span>
                </Col>
                <Col style={{display: "flex", justifyContent: "flex-end"}}>
                    <CloseButton onClick={()=>props.setShowModal(false)}/>
                </Col>
            </Row>
            
            {
              props.data.map((el,i)=>
                <Row style={{marginBottom: "10px"}} key={i}>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.username}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.minMoves}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "flex-end"}}>
                      
                  </Col>
                </Row>
              )
            }
        </TabPanel>
        <TabPanel value={value} index={1}>
            <Row style={{marginBottom: "20px"}}>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Username</span>
                </Col>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Turni Minimi</span>
                </Col >
                <Col style={{display: "flex", justifyContent: "flex-end"}}>
                    <CloseButton onClick={()=>props.setShowModal(false)} />
                </Col>
            </Row>
            {
              props.data.map((el,i)=>
                <Row style={{marginBottom: "10px"}} key={i}>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.username}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.minMoves}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "flex-end"}}>
                      
                  </Col>
                </Row>
              )
            }
        </TabPanel>
        <TabPanel value={value} index={2}>
            <Row style={{marginBottom: "20px"}}>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Username</span>
                </Col>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Rank</span>
                </Col>
                <Col style={{display: "flex", justifyContent: "flex-end"}}>
                    <CloseButton onClick={()=>props.setShowModal(false)} />
                </Col>
            </Row>
            {
              props.data.map((el,i)=>
                <Row style={{marginBottom: "10px"}} key={i}>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.username}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.rank}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "flex-end"}}>
                      
                  </Col>
                </Row>
              )
            }
        </TabPanel>
        <TabPanel value={value} index={3}>
            <Row style={{marginBottom: "20px"}}>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Username</span>
                </Col>
                <Col style={{display: "flex", justifyContent: "center"}}>
                    <span style={{fontWeight: "bold", fontSize: "22px"}}>Elo</span>
                </Col>
                <Col style={{display: "flex", justifyContent: "flex-end"}}>
                    <CloseButton onClick={()=>props.setShowModal(false)} />
                </Col>
            </Row>
            {
              props.data.map((el,i)=>
                <Row style={{marginBottom: "10px"}} key={i}>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.username}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "center"}}>
                      <span >{el.elo}</span>
                  </Col>
                  <Col style={{display: "flex", justifyContent: "flex-end"}}>
                      
                  </Col>
                </Row>
              )
            }
        </TabPanel>
      </div>
  
    </Box>
  );
}

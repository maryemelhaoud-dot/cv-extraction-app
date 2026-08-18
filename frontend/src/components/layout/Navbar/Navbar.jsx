import { Stepper, Step, StepLabel } from '@mui/material';
import './navbar.css';
import logoOcp from '../../../assets/logos/ocp-logo.png';

function Navbar({activeStep = 0 }) {
    const steps = [
        'Importer votre cv',
        'Extraction des informations',
        'Résultat et analyse'
    ];

    return (
    <div className="navbar">
    <div className="navbar-logo">
    <img src={logoOcp} alt="OCP" />
    </div>
    <div className="navbar-stepper">
    <Stepper activeStep={activeStep} alternativeLabel>
    {steps.map((label) => (
    <Step key={label}><StepLabel>{label}</StepLabel></Step>
  ))}
   </Stepper>
   </div>
   <div className="navbar-spacer"></div>
   </div>

    );
}

export default Navbar;
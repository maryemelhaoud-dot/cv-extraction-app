import Navbar from '../../components/layout/Navbar/Navbar';
import UploadZone from '../../components/upload/UploadZone/UploadZone';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import SdCardOutlinedIcon from '@mui/icons-material/SdCardOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

import './Upload.css';

function Upload() {
    return (
        <div className="upload-page">

            <Navbar activeStep={0} />

            <main className="upload-content">

                <UploadZone />

                <div className="upload-info">

                    <div className="info-item">
                        <DescriptionOutlinedIcon />
                        <p>Formats acceptés : PDF</p>
                    </div>

                    <div className="info-item">
                        <SdCardOutlinedIcon />
                        <p>Taille maximale : 10 Mo</p>
                    </div>

                    <div className="info-item">
                        <LockOutlinedIcon />
                        <p>Vos données sont sécurisées</p>
                    </div>

                </div>

            </main>

        </div>
    );
}

export default Upload;
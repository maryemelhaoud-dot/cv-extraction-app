import {BrowserRouter , Route , Routes} from 'react-router-dom';
import SplashScreen from '../pages/SplashScreen/SplashScreen';
import Upload from '../pages/Upload/Upload';
import Extraction from '../pages/Extraction/Extraction';
import Result from '../pages/Result/Result';
import NotFound from '../pages/NotFound/NotFound';


function AppRoutes(){
    return(
        <BrowserRouter>
        <Routes>
            <Route path='/' element={<SplashScreen/>}/>
            <Route path='/upload' element={<Upload/>}/>
            <Route path='/extraction' element={<Extraction/>}/>
            <Route path='/result' element={<Result/>}/>
            <Route path='*' element={<NotFound/>}/>
        </Routes>
        </BrowserRouter>
    );
}
export default AppRoutes;
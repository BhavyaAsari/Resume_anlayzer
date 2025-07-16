import Header from "./components/Header";
import Footer from "./components/Footer";
import ResumeUploader from "./components/ResumeUploader";
import "./App.css";

function App() {
  return (
    <div className="app-wrapper">
      <Header />
      <main className="main-wrapper">
        <div className="container">
          <ResumeUploader />
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default App;

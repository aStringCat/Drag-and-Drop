import FileUpload from "./FileUpload";
import "./App.css";

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Drag and Drop</h1>
      </header>
      <main>
        <FileUpload />
      </main>
    </div>
  );
};

export default App;

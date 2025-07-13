import React, { useState } from "react";
import axios from "axios";

function ResumeUploader() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [selectedSection, setSelectedSection] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [showRaw, setShowRaw] = useState(false);

  const handleChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return alert("Please select a PDF resume");

    const formData = new FormData();
    formData.append("resume", file);

    try {
      const res = await axios.post("http://localhost:5000/analyze-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(res.data);
      setError("");
      setSelectedSection("");
      setShowRaw(false);
    } catch (err) {
      setError("Something went wrong while uploading.");
      setResult(null);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError("");
    setSelectedSection("");
    setSearchQuery("");
    setShowRaw(false);
    document.querySelector('input[type="file"]').value = "";
  };

  const renderSection = () => {
    if (!result) return null;

    const sectionHeader = (title) => <h5 className="mt-4">{title}</h5>;

    switch (selectedSection) {
      case "personal":
        return (
          <>
            {sectionHeader("👤 Personal Details")}
            <div className="card p-3">
              <p><strong>Name:</strong> {result.name}</p>
              <p><strong>Email:</strong> {result.email}</p>
              <p><strong>Phone:</strong> {result.phone}</p>
            </div>
          </>
        );

      case "skills":
        return (
          <>
            {sectionHeader("🧠 Skills")}
            <div className="card p-3">
              {result.skills?.length ? (
                <ul className="list-group list-group-flush">
                  {result.skills.map((skill, i) => (
                    <li key={i} className="list-group-item">{skill}</li>
                  ))}
                </ul>
              ) : (
                <p>No skills found</p>
              )}
            </div>
          </>
        );

      case "education":
        return (
          <>
            {sectionHeader("🎓 Education")}
            <div className="card p-3">
              {result.education?.length ? (
                result.education.map((edu, i) => (
                  <div key={i} className="mb-3">
                    <p><strong>{edu.degree}</strong></p>
                    <p>{edu.organization}</p>
                    <p>{edu.start_date || "?"} — {edu.end_date || "?"}</p>
                    <p>Grade: {edu.grade || "N/A"}</p>
                    <hr />
                  </div>
                ))
              ) : (
                <p>No education records found.</p>
              )}
            </div>
          </>
        );

      case "career":
        return (
          <>
            {sectionHeader("💼 Career Suggestions")}
            <div className="card p-3">
              {result.career_suggestions?.length ? (
                <ul className="list-group list-group-flush">
                  {result.career_suggestions.map((s, i) => (
                    <li key={i} className="list-group-item">{s}</li>
                  ))}
                </ul>
              ) : (
                <p>No suggestions available.</p>
              )}
            </div>
          </>
        );

      case "search":
        const fullText = result.affinda_raw?.text || result.text_preview || "";
        const filtered = fullText
          .split("\n")
          .filter((line) => line.toLowerCase().includes(searchQuery.toLowerCase()));
        return (
          <>
            {sectionHeader("🔎 Keyword Search Results")}
            <input
              type="text"
              className="form-control mb-3"
              placeholder="e.g. internship, python, cloud"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="card p-3">
              {filtered.length ? (
                <ul className="list-group list-group-flush">
                  {filtered.map((line, i) => (
                    <li key={i} className="list-group-item">{line}</li>
                  ))}
                </ul>
              ) : (
                <p>No matches found.</p>
              )}
            </div>
          </>
        );

      default:
        const affindaData = result.affinda_raw || {};
        return (
          <>
            {sectionHeader("🗂️ Full Section-wise Data")}
            <div className="card p-3 mb-3">
              <h6>📝 Summary</h6>
              <p>{affindaData.summary || "Not available"}</p>
              <hr />
              <h6>🏢 Work Experience</h6>
              {affindaData.workExperience?.length ? (
                affindaData.workExperience.map((exp, i) => (
                  <div key={i} className="mb-2">
                    <p><strong>{exp.jobTitle?.raw || "Role"}</strong> at {exp.organisation || "Company"}</p>
                    <p>{exp.dates?.startDate || "Start"} - {exp.dates?.endDate || "End"}</p>
                    <p>{exp.jobDescription || ""}</p>
                    <hr />
                  </div>
                ))
              ) : <p>No work experience found</p>}
              <h6>🎯 Certifications</h6>
              {affindaData.certifications?.length ? (
                <ul>
                  {affindaData.certifications.map((cert, i) => (
                    <li key={i}>{cert.name}</li>
                  ))}
                </ul>
              ) : <p>No certifications listed</p>}
              <h6>🧪 Projects</h6>
              {affindaData.projects?.length ? (
                <ul>
                  {affindaData.projects.map((proj, i) => (
                    <li key={i}><strong>{proj.name}</strong>: {proj.highlights?.join(", ")}</li>
                  ))}
                </ul>
              ) : <p>No projects found</p>}
            </div>
          </>
        );
    }
  };

  return (
    <div className="container my-5">
      <h2 className="mb-4 text-center">📄 Resume Analyzer</h2>

      <div className="mb-3">
        <input type="file" accept=".pdf" onChange={handleChange} className="form-control" />
      </div>
      <div className="d-flex gap-2 mb-4">
        <button onClick={handleUpload} className="btn btn-primary">Upload Resume</button>
        <button onClick={handleReset} className="btn btn-secondary">Reset</button>
      </div>

      {error && <div className="alert alert-danger mt-3">{error}</div>}

      {result && (
        <>
          <h4 className="mb-2">📂 Select Section to View</h4>
          <select
            className="form-select mb-4"
            value={selectedSection}
            onChange={(e) => setSelectedSection(e.target.value)}
          >
            <option value="">🗂️ View Section-wise Output</option>
            <option value="personal">👤 Personal Details</option>
            <option value="skills">🧠 Skills</option>
            <option value="education">🎓 Education</option>
            <option value="career">💼 Career Suggestions</option>
            <option value="search">🔎 Search by Keyword</option>
          </select>

          {renderSection()}

          {result.note && (
            <div className="alert alert-warning mt-4">
              <strong>Note:</strong> {result.note}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ResumeUploader;

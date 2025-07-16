import React, { useState } from "react";
import {
  Upload,
  FileText,
  User,
  Brain,
  Search,
  BookOpen,
  Briefcase,
  Mail,
  Phone,
} from "lucide-react";

function ResumeUploader() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedSection, setSelectedSection] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const handleChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
    setResult(null);
    setSelectedSection("");
    setSearchQuery("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF resume");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("resume", file);

    try {
      const response = await fetch("http://localhost:5000/analyze-resume", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();

      if (data.status === "error") {
        setError(data.error || "Failed to analyze resume.");
        setResult(null);
      } else {
        let suggestions = data.career_suggestions;
        if (typeof suggestions === "string") {
          suggestions = suggestions.split("\n").filter(Boolean);
        }
        setResult({
          ...data,
          career_suggestions: suggestions,
        });
      }
    } catch (err) {
      console.error(err);
      setError("Server not reachable. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError("");
    setSelectedSection("");
    setSearchQuery("");
    setLoading(false);
    const input = document.querySelector('input[type="file"]');
    if (input) input.value = "";
  };

  const renderSection = () => {
    if (!result) return null;

    const InfoCard = ({ children }) => (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        {children}
      </div>
    );

    const sectionHeader = (title, icon) => (
      <div className="flex items-center gap-2 mb-4">
        {icon}
        <h4 className="text-xl font-semibold text-gray-800">{title}</h4>
      </div>
    );

    switch (selectedSection) {
      case "personal":
        return (
          <div>
            {sectionHeader("Personal Details", <User className="w-6 h-6 text-blue-600" />)}
            <InfoCard>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <User className="w-5 h-5 text-gray-600" />
                  <span className="font-medium">Name:</span>
                  <span>{result.name || "Not found"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-gray-600" />
                  <span className="font-medium">Email:</span>
                  <span>{result.email || "Not found"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Phone className="w-5 h-5 text-gray-600" />
                  <span className="font-medium">Phone:</span>
                  <span>{result.phone || "Not found"}</span>
                </div>
              </div>
            </InfoCard>
          </div>
        );

      case "skills":
        const softSkillKeywords = [
          "communication",
          "leadership",
          "teamwork",
          "adaptability",
          "problem-solving",
          "time management",
          "critical thinking",
          "creativity",
          "decision making",
          "empathy",
        ];
        const softSkills = result.skills?.filter((s) =>
          softSkillKeywords.some((k) =>
            s.toLowerCase().includes(k.toLowerCase())
          )
        ) || [];
        const techSkills =
          result.skills?.filter((s) => !softSkills.includes(s)) || [];

        return (
          <div>
            {sectionHeader("Skills", <Brain className="w-6 h-6 text-blue-600" />)}
            <div className="grid md:grid-cols-2 gap-6">
              <InfoCard>
                <h6 className="font-semibold mb-3 text-blue-700 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Technical Skills
                </h6>
                {techSkills.length ? (
                  <ul className="space-y-2 list-disc pl-5 text-gray-700">
  {techSkills.map((skill, i) => (
    <li key={i}>{skill}</li>
  ))}
</ul>

                ) : (
                  <p className="text-gray-500">No technical skills identified</p>
                )}
              </InfoCard>

              <InfoCard>
                <h6 className="font-semibold mb-3 text-green-700 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Soft Skills
                </h6>
                {softSkills.length ? (
                  <div className="flex flex-wrap gap-3">
                    {softSkills.map((skill, i) => (
                      <span
                        key={i}
                        className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No soft skills identified</p>
                )}
              </InfoCard>
            </div>
          </div>
        );

      case "education":
        return (
          <div>
            {sectionHeader("Education", <BookOpen className="w-6 h-6 text-blue-600" />)}
            <InfoCard>
              {result.education?.length ? (
                <div className="space-y-4">
                  {result.education.map((edu, i) => (
                    <div key={i} className="border-l-4 border-blue-500 pl-4">
                      <h6 className="font-semibold">{edu.degree}</h6>
                      <p>{edu.organization}</p>
                      <p className="text-sm text-gray-500">
                        {edu.start_date || "Start"} - {edu.end_date || "End"}
                      </p>
                      {edu.grade && (
                        <p className="text-sm text-gray-500">Grade: {edu.grade}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No education records found</p>
              )}
            </InfoCard>
          </div>
        );

      case "career":
        return (
          <div>
            {sectionHeader("Career Suggestions", <Briefcase className="w-6 h-6 text-blue-600" />)}
            <InfoCard>
              {result.career_suggestions?.length ? (
                <ul className="list-disc pl-5 text-gray-700 space-y-2">
                  {result.career_suggestions.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No suggestions found</p>
              )}
            </InfoCard>
          </div>
        );

      case "search":
        const allText = result.affinda_raw?.text || result.text_preview || "";
        const filtered = allText
          .split("\n")
          .filter((line) =>
            line.toLowerCase().includes(searchQuery.toLowerCase())
          );

        return (
          <div>
            {sectionHeader("Search Resume Text", <Search className="w-6 h-6 text-blue-600" />)}
            <input
              type="text"
              placeholder="Search keywords like python, cloud..."
              className="w-full p-3 mb-4 border border-gray-300 rounded-lg"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <InfoCard>
              {filtered.length ? (
                <ul className="list-disc pl-5 space-y-2 text-gray-700 max-h-96 overflow-y-auto">
                  {filtered.map((line, i) => (
                    <li key={i}>{line}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No results matched your search</p>
              )}
            </InfoCard>
          </div>
        );

      default:
        return null;
    }
  };

 return (
  <div className="min-h-screen flex flex-col bg-gray-100">
    <main className="flex-1 max-w-3xl w-full mx-auto px-6 py-10">
      <div className="bg-white p-8 shadow-xl rounded-xl border border-gray-200">
        <h2 className="text-2xl font-bold mb-8 flex items-center gap-3 text-gray-800">
          <FileText className="w-7 h-7 text-blue-600" />
          Upload Your Resume
        </h2>

        <div className="flex flex-col md:flex-row md:items-center gap-4 mb-6">
          <input
            type="file"
            accept=".pdf"
            onChange={handleChange}
            className="file:bg-blue-600 file:text-white file:rounded-md file:border-0 file:px-4 file:py-2 file:mr-4 
                       border border-gray-300 rounded-md w-full md:w-auto p-2 bg-white text-sm shadow-sm"
          />

          <button
            onClick={handleUpload}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md shadow hover:bg-blue-700 transition disabled:opacity-50"
          >
            <Upload className="w-5 h-5" />
            {loading ? "Analyzing..." : "Upload Resume"}
          </button>

          <button
            onClick={handleReset}
            className="bg-gray-600 text-white px-4 py-2 rounded-md shadow hover:bg-gray-700 transition"
          >
            Reset
          </button>
        </div>

        {error && (
          <div className="bg-red-100 text-red-800 px-4 py-3 rounded-md mb-4 border border-red-300">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-6 mt-6">
            <label className="font-semibold text-gray-700 block mb-2">
              📂 Select Section to View
            </label>
            <select
              className="w-full border border-gray-300 rounded-md p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
            >
              <option value="">Select...</option>
              <option value="personal">👤 Personal Details</option>
              <option value="skills">🧠 Skills</option>
              <option value="education">🎓 Education</option>
              <option value="career">💼 Career Suggestions</option>
              <option value="search">🔍 Search Keywords</option>
            </select>

            {renderSection()}
          </div>
        )}
      </div>
    </main>
  </div>
);
    
   
}

export default ResumeUploader;

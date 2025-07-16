import React, { useState, useEffect } from "react";
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
  BarChart2,
  Lightbulb,
  Settings,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

function ResumeUploader() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedSection, setSelectedSection] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [industryTrends, setIndustryTrends] = useState("");

  const handleChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
    setResult(null);
    setSelectedSection("");
    setSearchQuery("");
    setIndustryTrends("");
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

  const fetchIndustryTrends = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:5000/industry-trends", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ skills: result.skills || [] }),
      });
      const data = await res.json();
      setIndustryTrends(data.trends || "No trends available.");
    } catch (e) {
      setIndustryTrends("Failed to fetch trends.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (
      selectedSection === "industry" &&
      !industryTrends &&
      result?.skills?.length > 0
    ) {
      fetchIndustryTrends();
    }
  }, [selectedSection, industryTrends, result]);

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError("");
    setSelectedSection("");
    setSearchQuery("");
    setLoading(false);
    setIndustryTrends("");
    const input = document.querySelector('input[type="file"]');
    if (input) input.value = "";
  };

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

  const categorizeSkills = (skills) => {
    const frontend = ["react", "html", "css", "javascript", "vue", "angular"];
    const backend = ["node", "django", "flask", "spring", "express"];
    const programming = ["python", "java", "c++", "javascript"];
    const otherTech = ["git", "docker", "aws", "azure", "gcp", "sql", "mongodb"];
    const soft = ["communication", "teamwork", "leadership", "problem-solving"];

    const categorized = {
      Frontend: [],
      Backend: [],
      Programming: [],
      OtherTech: [],
      SoftSkills: [],
    };

    skills.forEach((skill) => {
      const normalized = skill.trim().toLowerCase();
      const matchCategory = (keywords) =>
        keywords.some((keyword) => normalized.includes(keyword));

      if (matchCategory(frontend)) categorized.Frontend.push(skill);
      else if (matchCategory(backend)) categorized.Backend.push(skill);
      else if (matchCategory(programming)) categorized.Programming.push(skill);
      else if (matchCategory(otherTech)) categorized.OtherTech.push(skill);
      else if (matchCategory(soft)) categorized.SoftSkills.push(skill);
    });

    return categorized;
  };

  const renderSection = () => {
    if (!result) return null;

    const skillsCategorized = categorizeSkills(result.skills || []);

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

      case "tech-skills":
        return (
          <div>
            {sectionHeader("Technical Skills", <Settings className="w-6 h-6 text-blue-600" />)}
            <InfoCard>
              {["Frontend", "Backend", "Programming", "OtherTech"].map((cat) =>
                skillsCategorized[cat]?.length ? (
                  <div key={cat} className="mb-4">
                    <h5 className="text-md font-semibold text-gray-700 mb-2">{cat}:</h5>
                    <ul className="list-disc pl-5 text-gray-800 space-y-1">
                      {skillsCategorized[cat].map((skill, i) => (
                        <li key={i}>{skill}</li>
                      ))}
                    </ul>
                  </div>
                ) : null
              )}
            </InfoCard>
          </div>
        );

      case "soft-skills":
        return (
          <div>
            {sectionHeader("Soft Skills", <Brain className="w-6 h-6 text-blue-600" />)}
            <InfoCard>
              {skillsCategorized.SoftSkills?.length ? (
                <ul className="list-disc pl-5 text-gray-700 space-y-1">
                  {skillsCategorized.SoftSkills.map((skill, i) => (
                    <li key={i}>{skill}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No soft skills found</p>
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

      case "ai-advice":
        return (
          <div>
            {sectionHeader("AI Career Advice", <Lightbulb className="w-6 h-6 text-yellow-600" />)}
            <InfoCard>
              {result.ai_agent_career_advice ? (
                <div className="prose prose-sm max-w-none text-gray-800">
  <ReactMarkdown>{result.ai_agent_career_advice}</ReactMarkdown>
</div>
              
              ) : (
                <p className="text-gray-500">No AI advice available</p>
              )}
            </InfoCard>
          </div>
        );

      case "industry":
        return (
          <div>
            {sectionHeader("Industry Trends", <BarChart2 className="w-6 h-6 text-blue-600" />)}
            <InfoCard>
              {industryTrends ? (

                <div className="prose prose-sm max-w-none text-gray-800">
  <ReactMarkdown>{industryTrends}</ReactMarkdown>
</div>

               
              ) : (
                <p className="text-gray-500">Loading industry insights...</p>
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
                <option value="tech-skills">💻 Technical Skills</option>
                <option value="soft-skills">🌱 Soft Skills</option>
                <option value="career">💼 Career Suggestions</option>
                <option value="ai-advice">🧠 AI Career Advice</option>
                <option value="industry">📊 Industry Trends</option>
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

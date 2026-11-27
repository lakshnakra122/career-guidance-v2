import { Navigate, Route, Routes } from 'react-router-dom'
import Home, { CareersPreview } from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Assessment from './pages/Assessment'
import Careers from './pages/Careers'
import SkillGap from './pages/SkillGap'
import Roadmap from './pages/Roadmap'
import StudyPlan from './pages/StudyPlan'
import Chat from './pages/Chat'
import Profile from './pages/Profile'
import AdminUsers from './pages/AdminUsers'
import ProtectedRoute from './components/ProtectedRoute'
import { AppLayout } from './components/ui'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/careers-preview" element={<CareersPreview />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/app" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="assessment" element={<Assessment />} />
        <Route path="careers" element={<Careers />} />
        <Route path="skill-gap" element={<SkillGap />} />
        <Route path="roadmap" element={<Roadmap />} />
        <Route path="study-plan" element={<StudyPlan />} />
        <Route path="chat" element={<Chat />} />
        <Route path="profile" element={<Profile />} />
        <Route path="admin" element={<AdminUsers />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

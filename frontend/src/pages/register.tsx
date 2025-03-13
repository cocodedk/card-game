import React from 'react';
import PlayerRegistration from '../components/PlayerRegistration';
import AuthLayout from '../components/AuthLayout';

const RegisterPage: React.FC = () => {
  return (
    <AuthLayout
      title="Join the Card Game"
      description="Create your account and choose your callsign to start playing today"
      showRegisterLink={false}
    >
      <PlayerRegistration />
    </AuthLayout>
  );
};

export default RegisterPage;

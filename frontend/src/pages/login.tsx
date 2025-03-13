import React from 'react';
import LoginForm from '../components/LoginForm';
import AuthLayout from '../components/AuthLayout';

const LoginPage: React.FC = () => {
  return (
    <AuthLayout
      title="Welcome Back"
      description="Sign in to your account to continue playing"
      showLoginLink={false}
    >
      <LoginForm />
    </AuthLayout>
  );
};

export default LoginPage;

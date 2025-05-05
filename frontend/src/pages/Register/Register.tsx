import { FC, useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Register.module.scss';
import { 
  AuthLayout, 
  InputField, 
  Button, 
  EmailIcon, 
  LockIcon,
  EyeIcon,
  EyeOffIcon
} from '../../components';
import { ROUTES } from '../../routes';
import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import { register, clearError } from '../../redux/auth';

// Using Record<string, never> instead of empty interface
type RegisterProps = Record<string, never>;

export const Register: FC<RegisterProps> = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { loading, error, isAuthenticated } = useAppSelector(state => state.auth);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  // If user is already authenticated, redirect to the home page
  useEffect(() => {
    if (isAuthenticated) {
      navigate(ROUTES.HOME);
    }
  }, [isAuthenticated, navigate]);

  // Reset server errors when input fields change
  useEffect(() => {
    if (error) {
      dispatch(clearError());
    }
  }, [email, password, confirmPassword, dispatch, error]);

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(prev => !prev);
  };

  const validateForm = (): boolean => {
    const newErrors: {
      email?: string;
      password?: string;
      confirmPassword?: string;
    } = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    // Send registration request through Redux
    dispatch(register({ email, password }));
  };

  const goToLogin = () => {
    navigate(ROUTES.LOGIN);
  };

  return (
    <AuthLayout 
      title="Registration" 
      subtitle="Create an account to access the service"
    >
      <form className={styles.form} onSubmit={handleSubmit}>
        {error && (
          <div className={styles.serverError}>
            {error}
          </div>
        )}
        
        <InputField
          label="Email"
          icon={<EmailIcon />}
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          error={formErrors.email}
        />
        
        <InputField
          label="Password"
          icon={<LockIcon />}
          type={showPassword ? 'text' : 'password'}
          placeholder="Minimum 8 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          error={formErrors.password}
          rightIcon={showPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={togglePasswordVisibility}
        />
        
        <InputField
          label="Confirm Password"
          icon={<LockIcon />}
          type={showConfirmPassword ? 'text' : 'password'}
          placeholder="Repeat password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          error={formErrors.confirmPassword}
          rightIcon={showConfirmPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={toggleConfirmPasswordVisibility}
        />
        
        <Button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
        >
          {loading ? 'Registering...' : 'Register'}
        </Button>
        
        <div className={styles.loginPrompt}>
          <span>Already have an account?</span>
          <button 
            type="button" 
            className={styles.loginLink}
            onClick={goToLogin}
          >
            Log in
          </button>
        </div>
      </form>
    </AuthLayout>
  );
}; 
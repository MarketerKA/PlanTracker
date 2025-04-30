import { FC, useState, FormEvent } from 'react';
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

export interface RegisterProps {}

export const Register: FC<RegisterProps> = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<{
    email?: string;
    verificationCode?: string;
    password?: string;
    confirmPassword?: string;
  }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(prev => !prev);
  };

  const validateForm = () => {
    const newErrors: {
      email?: string;
      verificationCode?: string;
      password?: string;
      confirmPassword?: string;
    } = {};
    
    if (!email) {
      newErrors.email = 'Email обязателен';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Некорректный email';
    }
    
    if (codeSent && !verificationCode) {
      newErrors.verificationCode = 'Введите код подтверждения';
    }
    
    if (!password) {
      newErrors.password = 'Пароль обязателен';
    } else if (password.length < 6) {
      newErrors.password = 'Пароль должен содержать минимум 6 символов';
    }
    
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Пароли не совпадают';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const sendVerificationCode = async () => {
    // Проверка только email
    const emailError = email ? (!/\S+@\S+\.\S+/.test(email) ? 'Некорректный email' : '') : 'Email обязателен';
    
    if (emailError) {
      setErrors(prev => ({ ...prev, email: emailError }));
      return;
    }
    
    setIsVerifying(true);
    
    try {
      // Имитация отправки кода на email
      console.log('Отправка кода подтверждения на:', email);
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setCodeSent(true);
      alert(`Код подтверждения отправлен на ${email}. (В демо версии используйте код: 123456)`);
    } catch (error) {
      console.error('Ошибка при отправке кода:', error);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      // Проверим код подтверждения (в реальном приложении это будет API-запрос)
      if (verificationCode !== '123456') {
        setErrors(prev => ({ ...prev, verificationCode: 'Неверный код подтверждения' }));
        setIsLoading(false);
        return;
      }
      
      // Здесь будет запрос на регистрацию
      console.log('Регистрация с данными:', { email, password });
      
      // Имитация API-запроса
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // В реальном приложении здесь будет обработка ответа от API
      console.log('Успешная регистрация');
      
      // Перенаправление на страницу входа
      navigate(ROUTES.LOGIN);
    } catch (error) {
      console.error('Ошибка при регистрации:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const goToLogin = () => {
    navigate(ROUTES.LOGIN);
  };

  return (
    <AuthLayout 
      title="Регистрация" 
      subtitle="Создайте аккаунт для доступа к сервису"
    >
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.emailContainer}>
          <InputField
            label="Email"
            icon={<EmailIcon />}
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            error={errors.email}
            disabled={codeSent}
          />
          {!codeSent && (
            <Button 
              type="button" 
              variant="secondary"
              onClick={sendVerificationCode}
              disabled={isVerifying}
              className={styles.sendCodeButton}
            >
              {isVerifying ? 'Отправка...' : 'Отправить код'}
            </Button>
          )}
        </div>
        
        {codeSent && (
          <InputField
            label="Код подтверждения"
            type="text"
            placeholder="Введите код из письма"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            required
            error={errors.verificationCode}
          />
        )}
        
        <InputField
          label="Пароль"
          icon={<LockIcon />}
          type={showPassword ? 'text' : 'password'}
          placeholder="Минимум 6 символов"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          error={errors.password}
          rightIcon={showPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={togglePasswordVisibility}
        />
        
        <InputField
          label="Подтверждение пароля"
          icon={<LockIcon />}
          type={showConfirmPassword ? 'text' : 'password'}
          placeholder="Повторите пароль"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          error={errors.confirmPassword}
          rightIcon={showConfirmPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={toggleConfirmPasswordVisibility}
        />
        
        <Button
          type="submit"
          disabled={isLoading || !codeSent}
          className={styles.submitButton}
        >
          {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
        </Button>
        
        <div className={styles.loginPrompt}>
          <span>Уже есть аккаунт?</span>
          <button 
            type="button" 
            className={styles.loginLink}
            onClick={goToLogin}
          >
            Войти
          </button>
        </div>
      </form>
    </AuthLayout>
  );
}; 
import axios from "axios";
import {
  SIGNUP_REQUEST,
  SIGNUP_SUCCESS,
  SIGNUP_FAILURE,
  LOGIN_REQUEST,
  LOGIN_SUCCESS,
  LOGIN_FAILURE,
  GET_USER_REQUEST,
  GET_USER_SUCCESS,
  GET_USER_FAILURE,
  LOGOUT,
  GET_ALL_CUSTOMERS_REQUEST,
  GET_ALL_CUSTOMERS_SUCCESS,
  GET_ALL_CUSTOMERS_FAILURE,
} from "./ActionTypes";
import { API_BASE_URL } from "../../Config/api";

const extractErrorMessage = (error) => {
  if (error.response && error.response.data) {
    const errorMessage = error.response.data.error || error.response.data.message;
    return errorMessage.replace(/^[^:]+:\s*/, "").replace(/;\s*$/, "").trim();
  }
  return error.message;
};

const signupRequest = () => ({ type: SIGNUP_REQUEST });
const signupSuccess = (user) => ({ type: SIGNUP_SUCCESS, payload: user });
const signupFailure = (error) => ({ type: SIGNUP_FAILURE, payload: error });

export const signup = (userData) => async (dispatch) => {
  dispatch(signupRequest());
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/signup`, userData);
    const user = response.data;
    if (user.jwt) localStorage.setItem("jwt", user.jwt);
    dispatch(signupSuccess(user));
  } catch (error) {
    const errorMessage = extractErrorMessage(error);
    dispatch(signupFailure(errorMessage));
  }
};

const loginRequest = () => ({ type: LOGIN_REQUEST });
const loginSuccess = (user) => ({ type: LOGIN_SUCCESS, payload: user });
const loginFailure = (error) => ({ type: LOGIN_FAILURE, payload: error });

export const login = (userData) => async (dispatch) => {
  dispatch(loginRequest());
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, userData);
    const user = response.data;
    if (user.jwt) localStorage.setItem("jwt", user.jwt);
    dispatch(loginSuccess(user));
    window.location.reload()
  } catch (error) {
    const errorMessage = extractErrorMessage(error);
    dispatch(loginFailure(errorMessage));
  }
};

export const getUser = (token) => async (dispatch) => {
  dispatch({ type: GET_USER_REQUEST });
  try {
    const response = await axios.get(`${API_BASE_URL}/api/users/profile`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const user = response.data;
    dispatch({ type: GET_USER_SUCCESS, payload: user });
  } catch (error) {
    const errorMessage = extractErrorMessage(error);
    dispatch({ type: GET_USER_FAILURE, payload: errorMessage });
  }
};

export const getAllCustomers = (token) => async (dispatch) => {
  dispatch({ type: GET_ALL_CUSTOMERS_REQUEST });
  try {
    const response = await axios.get(`${API_BASE_URL}/api/admin/users`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const users = response.data;
    dispatch({ type: GET_ALL_CUSTOMERS_SUCCESS, payload: users });
  } catch (error) {
    const errorMessage = extractErrorMessage(error);
    dispatch({ type: GET_ALL_CUSTOMERS_FAILURE, payload: errorMessage });
  }
};

export const logout = () => (dispatch) => {
  dispatch({ type: LOGOUT });
  localStorage.clear();
};

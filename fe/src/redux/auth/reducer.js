import {
    LOGIN_REQUEST,
    LOGIN_SUCCESS,
    LOGIN_FAILURE,
    LOGOUT,
} from "./actionTypes";

const initialState = {
    user: null,
    isLoading: false,
    error: null,
    customers: [],
};

const authReducer = (state = initialState, action) => {
    switch (action.type) {
        case LOGIN_REQUEST:
            return { ...state, isLoading: true, error: null };
            
        case LOGIN_FAILURE:
            return { ...state, isLoading: false, error: action.payload };

        case LOGIN_SUCCESS:
            return { ...state, isLoading: false };

        case LOGOUT:
            localStorage.removeItem("jwt");
            return { ...state, jwt: null, user: null };

        default:
            return state;
    }
};

export default authReducer;


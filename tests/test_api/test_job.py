import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from api.routes.job import create_job_posting
from exceptions.exceptions import DatabaseException


JOB_POSTING_DATA = {
    'valid_return': {
        'id': 3,
        'posted_at': '2024-10-14 18:10:05.008030',
        'company_name': 'watchGuard',
        'job_description': 'sde role',
        'ctc': 9.4,
        'applicable_degree': 'bachelor of technology',
        'applicable_branches': ['computer science and engineering', 'electrical engineering'],
        'total_round_count': 4,
        'current_round': 0,
        'application_closed_on': '2024-10-15 07:37:41.000000'
    },
    'valid_input': {
        'company_name': 'watchGuard',
        'job_description': 'sde role',
        'ctc': 9.4,
        'applicable_degree': 'bachelor of technology',
        'applicable_branches': ['computer science and engineering', 'electrical engineering'],
        'total_round_count': 4,
        'application_closed_on': '2024-10-15 07:37:41.000000'
    }
}


class TestJob:
    def setup_method(self):
        mock_logger = MagicMock()
        mock_logger.log = MagicMock(return_value=None)

        self.request = MagicMock()
        self.request.state.log = mock_logger

        self.mock_user_functionality = MagicMock()

    @pytest.fixture
    def mock_create_job_request_valid(self):
        mock_create_job_request = MagicMock()
        mock_create_job_request.model_dump.return_value = JOB_POSTING_DATA['valid_input']

        return mock_create_job_request

    @pytest.fixture
    def mock_user_functionality(self):
        mock_user_functionality = MagicMock()
        return mock_user_functionality

    def test_create_job_posting_valid_request_data_success(self, mock_create_job_request_valid,
                                                           mock_user_functionality):
        # Arrange
        expected_result = JOB_POSTING_DATA['valid_return']
        mock_user_functionality.create_job_posting.return_value = JOB_POSTING_DATA['valid_return']

        # Act
        result = create_job_posting(mock_user_functionality, mock_create_job_request_valid,  self.request)

        # Assert
        assert result == expected_result
        mock_user_functionality.create_job_posting.assert_called_once_with(JOB_POSTING_DATA['valid_input'])

    def test_create_job_posting_database_exception_http_exception_500(self, mock_create_job_request_valid,
                                                                      mock_user_functionality):
        # Arrange
        mock_user_functionality.create_job_posting = MagicMock()
        mock_user_functionality.create_job_posting.side_effect = DatabaseException

        # Act and Assert
        with pytest.raises(HTTPException) as exception:
            result = create_job_posting(mock_user_functionality, mock_create_job_request_valid, self.request)

        # Arrange
        assert exception.value.status_code == 500

    def test_create_job_posting_general_exception_http_exception_500(self, mock_create_job_request_valid,
                                                                     mock_user_functionality):
        # Arrange
        mock_user_functionality.create_job_posting = MagicMock()
        mock_user_functionality.create_job_posting.side_effect = Exception

        # Act and Assert
        with pytest.raises(HTTPException) as exception:
            result = create_job_posting(mock_user_functionality, mock_create_job_request_valid, self.request)

        # Arrange
        assert exception.value.status_code == 500




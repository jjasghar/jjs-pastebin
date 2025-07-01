"""
Tests for CLI functionality.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from cli.jj import cli as cli_main
from click.testing import CliRunner


class TestCLI:
    """Test CLI functionality."""
    
    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli_main, ['--help'])
        
        assert result.exit_code == 0
        assert 'Usage:' in result.output
        assert 'paste' in result.output.lower()
    
    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli_main, ['--help'])
        
        assert result.exit_code == 0
        assert 'Usage:' in result.output
        assert 'paste' in result.output.lower()
    
    @patch('requests.post')
    def test_paste_file(self, mock_post):
        """Test pasting a file via CLI."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'unique_id': 'test123',
            'url': 'http://localhost:8000/paste/test123'
        }
        mock_post.return_value = mock_response
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("Hello, World!")')
            temp_file = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(cli_main, [
                'paste', temp_file,
                '--api-url', 'http://localhost:8000/api'
            ])
            
            assert result.exit_code == 0
            assert 'test123' in result.output
            mock_post.assert_called_once()
        finally:
            os.unlink(temp_file)
    
    @patch('requests.post')
    def test_paste_stdin(self, mock_post):
        """Test pasting from stdin via CLI."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'unique_id': 'stdin123',
            'url': 'http://localhost:8000/paste/stdin123'
        }
        mock_post.return_value = mock_response
        
        runner = CliRunner()
        result = runner.invoke(cli_main, [
            'paste', '-',
            '--api-url', 'http://localhost:8000/api'
        ], input='console.log("Hello from stdin");')
        
        assert result.exit_code == 0
        assert 'stdin123' in result.output
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_paste_with_title(self, mock_post):
        """Test pasting with custom title."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'unique_id': 'title123',
            'url': 'http://localhost:8000/paste/title123'
        }
        mock_post.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write('console.log("test");')
            temp_file = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(cli_main, [
                'paste', temp_file,
                '--title', 'My Custom Title',
                '--api-url', 'http://localhost:8000/api'
            ])
            
            assert result.exit_code == 0
            
            # Check that title was included in API call
            call_args = mock_post.call_args
            data = call_args[1]['json']  # Using json parameter, not data
            assert data['title'] == 'My Custom Title'
        finally:
            os.unlink(temp_file)
    
    @patch('requests.post')
    def test_paste_private(self, mock_post):
        """Test creating private paste."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'unique_id': 'private123',
            'url': 'http://localhost:8000/paste/private123'
        }
        mock_post.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('secret code')
            temp_file = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(cli_main, [
                'paste', temp_file,
                '--private',
                '--api-url', 'http://localhost:8000/api'
            ])
            
            assert result.exit_code == 0
            
            # Check that private flag was included
            call_args = mock_post.call_args
            data = call_args[1]['json']
            assert data['is_public'] is False
        finally:
            os.unlink(temp_file)
    
    @patch('requests.post')
    def test_language_detection(self, mock_post):
        """Test automatic language detection from file extension."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'unique_id': 'lang123',
            'url': 'http://localhost:8000/paste/lang123'
        }
        mock_post.return_value = mock_response
        
        # Test Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def hello(): pass')
            temp_file = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(cli_main, [
                'paste', temp_file,
                '--api-url', 'http://localhost:8000/api'
            ])
            
            assert result.exit_code == 0
            
            # Check that language was detected
            call_args = mock_post.call_args
            data = call_args[1]['json']
            assert data['language'] == 'python'
        finally:
            os.unlink(temp_file)
    
    @patch('requests.post')
    def test_auth_failure(self, mock_post):
        """Test authentication failure handling."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Unauthorized'}
        mock_post.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test')
            temp_file = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(cli_main, [
                'paste', temp_file,
                '--api-url', 'http://localhost:8000/api'
            ])
            
            assert result.exit_code != 0
            assert 'unauthorized' in result.output.lower() or 'error' in result.output.lower()
        finally:
            os.unlink(temp_file)
    
    def test_cli_commands_exist(self):
        """Test that CLI commands exist."""
        runner = CliRunner()
        result = runner.invoke(cli_main, ['--help'])
        
        assert result.exit_code == 0
        assert 'paste' in result.output
        assert 'login' in result.output
        assert 'logout' in result.output
    
    def test_missing_file(self):
        """Test handling of missing file."""
        runner = CliRunner()
        result = runner.invoke(cli_main, [
            'paste', 'nonexistent.txt'
        ])
        
        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()
    
    def test_paste_help(self):
        """Test paste command help."""
        runner = CliRunner()
        result = runner.invoke(cli_main, ['paste', '--help'])
        
        assert result.exit_code == 0
        assert 'title' in result.output.lower()
        assert 'language' in result.output.lower()
        assert 'private' in result.output.lower()


class TestCLIIntegration:
    """Integration tests for CLI with actual server."""
    
    @pytest.mark.integration
    @patch('requests.post')
    def test_full_workflow(self, mock_post):
        """Test complete CLI workflow."""
        # Mock successful paste creation
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'unique_id': 'workflow123',
            'url': 'http://localhost:8000/paste/workflow123'
        }
        mock_post.return_value = mock_response
        
        # Create test file
        test_content = '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(cli_main, [
                'paste', temp_file,
                '--title', 'Fibonacci Function',
                '--api-url', 'http://localhost:8000/api'
            ])
            
            assert result.exit_code == 0
            assert 'workflow123' in result.output
            
            # Verify API call was made correctly
            call_args = mock_post.call_args
            assert call_args[0][0] == 'http://localhost:8000/api/pastes'
            
            data = call_args[1]['json']
            assert data['title'] == 'Fibonacci Function'
            assert data['language'] == 'python'
            assert 'fibonacci' in data['content']
            
        finally:
            os.unlink(temp_file) 
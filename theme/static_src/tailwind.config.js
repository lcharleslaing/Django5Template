module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '!../../**/node_modules',
        '../../**/*.js',
        '../../**/*.py'
    ],
    plugins: [
        require('daisyui'),
    ],
}

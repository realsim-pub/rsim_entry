#include <glog/logging.h>

#ifndef PYTHON_LOGGER_H_
#define PYTHON_LOGGER_H_

namespace matrix{
class PythonLogger : public google::LogSink {
 public:
  virtual void send(google::LogSeverity severity, const char* /* full_filename */,
                    const char* base_filename, int line,
                    const struct ::tm* tm_time,
                    const char* message, size_t message_len);
};

PythonLogger *PyLogger();

}

#define PY_INFO LOG_TO_SINK_BUT_NOT_TO_LOGFILE(matrix::PyLogger(), INFO) 
#define PY_WARN LOG_TO_SINK_BUT_NOT_TO_LOGFILE(matrix::PyLogger(), WARNING) 
#define PY_ERROR LOG_TO_SINK_BUT_NOT_TO_LOGFILE(matrix::PyLogger(), ERROR)
#define PY_FATAL LOG_TO_SINK_BUT_NOT_TO_LOGFILE(matrix::PyLogger(), FATAL)

#endif